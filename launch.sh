#!/bin/bash
# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.
#


VCPMEM="${VCPMEM:-1024}"
VCPU="${VCPU:-1}"
ID="${ID:-$HOSTNAME}"
NUMANODE="${NUMANOdE:-0}"

echo 1 > /var/jnx/docker
JUNOSDIR=/home/pfe/junos
PFE_SRC=/usr/share/pfe

echo -n "Juniper Networks vMX lwaftr Docker Container "
cat /VERSION
echo ""

set -e	#  Exit immediately if a command exits with a non-zero status.

echo "/u contains the following files:"
ls /u

echo "Launching with arguments: $@"

while getopts "h?V:m:c:l:p:I:R:d" opt; do
  case "$opt" in
    h|\?)
      show_help
      exit 1
      ;;
    V)  VCPU=$OPTARG
      ;;
    m)  VCPMEM=$OPTARG
      ;;
    c)  CONFIG=$OPTARG
      ;;
    l)  LICENSE=$OPTARG
      ;;
    p)  PUBLICKEY=$OPTARG
      ;;
    I)  IDENTITY=$OPTARG
      ;;
    R)  QEMUVCPCPUS=$OPTARG
      ;;
    d)  DEBUG=1
      ;;
  esac
done

CONFIG="${CONFIG-config.txt}"

shift "$((OPTIND-1))"

if [ ! -z "$1" ]; then
  IMAGE=$1
  shift
fi

if [ ! -f "/u/$IMAGE" ]; then
  echo "vMX tar file $IMAGE not found"
  exit 1
fi

HPFREE=$(cat /proc/meminfo |grep HugePages_Free|awk {'print $2'})
if [ $HPFREE = 0 ]; then
   echo 'no free HugePages found. Need those to run forwarding engine:'
   cat /proc/meminfo|grep Huge
   exit 1
fi

ROOTPASSWORD=$(pwgen 24 1)
SALT=$(pwgen 8 1)
HASH=$(openssl passwd -1 -salt $SALT $ROOTPASSWORD)
myip=$(ifconfig eth0|grep 'inet addr'|cut -d: -f2|awk '{print $1}')
echo "-----------------------------------------------------------------------"
echo "vMX $ID ($myip) root password to $ROOTPASSWORD"
echo "-----------------------------------------------------------------------"
echo ""

# fix network interface order due to https://github.com/docker/compose/issues/4645
/fix_network_order.sh

if [[ "$IMAGE" =~ \.qcow2$ ]]; then
  echo "using qcow2 image $IMAGE"
  cp /u/$IMAGE /tmp/
  VCPIMAGE=$IMAGE
else
  echo "extracting qcow2 image from $IMAGE ..."
  tar zxvf /u/$IMAGE -C /tmp/ --wildcards vmx/images/junos*qcow2 2>/dev/null
  VCPIMAGE=$(ls /tmp/vmx*/images/junos*qcow2)
  mv $VCPIMAGE /tmp/
  VCPIMAGE=${VCPIMAGE##*/}
fi

if [ ! -f "/u/$LICENSE" ]; then
  echo "Warning: No license file found ($LICENSE)"
else
  echo "using license keys in $LICENSE"
fi

# loop thru ethernet interfaces and bridge eth0 to tap fxp0, remove its IP
# and build matching junos config

ethlist=$(netstat -i|grep eth|cut -d' ' -f1 | paste -sd " " -)
echo "ethernet interfaces: $ethlist"

echo "creating ssh public/private keypair to communicate with Junos"
ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''
JETPUBKEY=$(cat /root/.ssh/id_rsa.pub)

if [ ! -f "/u/$PUBLICKEY" ]; then
  echo "WARNING: Can't read ssh public key file $PUBLICKEY"
  SSHPUBLIC=$JETPUBKEY  # to keep junos config parser happy
else
  SSHPUBLIC=$(cat /u/$PUBLICKEY)
fi

cat > /tmp/$CONFIG <<EOF
system {
  host-name $ID;
  root-authentication {
    encrypted-password "$HASH";
    ssh-rsa "$SSHPUBLIC";
    ssh-rsa "$JETPUBKEY";
  }
  services {
    ssh {
      client-alive-interval 30;
    }
    netconf {
      ssh;
    }
  }
}
EOF

# append user provided config. Doing this after our initial settings ubove
# allows a user to overwrite our defaults, like host-name
if [ -f /u/$CONFIG ]; then
  cat /u/$CONFIG >> /tmp/$CONFIG
fi

if [ ! -z "$SSHPUBLIC" ]; then
  SSHUSER=$(echo $SSHPUBLIC | cut -d' ' -f3 | cut -d'@' -f1)
  echo "adding super-user $SSHUSER with public key $SSHPUBLIC to config"
  cat >> /tmp/$CONFIG <<EOF
system {
  root-authentication {
    ssh-rsa "$SSHPUBLIC";
  }
EOF
  if [ "$SSHUSER" != "root" ]; then
    # only do this for non-root logins
    cat >> /tmp/$CONFIG <<EOF
  login {
    user $SSHUSER {
      class super-user;
      authentication {
        encrypted-password "$HASH";
        ssh-rsa "$SSHPUBLIC";
      }
    }
  }
EOF
  fi
  cat >> /tmp/$CONFIG <<EOF
}
EOF
fi
cat >> /tmp/$CONFIG <<EOF
groups {
  docker-networking {
    protocols {
      lldp {
        interface all;
      }
    }
    interfaces {
EOF

ifdescrlist=$(docker inspect --format='{{range $p, $conf := .NetworkSettings.Networks}} {{$p}}  {{end}}' $HOSTNAME)
echo "ifdescr array = $ifdescrlist"
IFS=' ' read -r -a ifdarray <<< "$ifdescrlist"

index=0
ifdindex=0
for eth in $ethlist; do
  echo "$eth ..."
  myip=$(ifconfig $eth|grep 'inet addr'|cut -d: -f2|awk '{print $1}')
  myipmask=$(ip -o -f inet addr show $eth |awk '{print $4}')
  ifdescr="${ifdarray[$ifdindex]}"
  ifdindex=$(($ifdindex + 1))
  echo "ifdescr=$ifdescr"
  if [ "eth0" == $eth ]; then
    mygw=$(ip -4 route list 0/0 |cut -d' ' -f3)
    mymac=$(ifconfig $eth |grep HWaddr|awk {'print $5'})
    echo "Bridging $eth ($myipmask/$mymac) with fxp0"
    brctl addbr br-ext
    ip link set up br-ext
    ip tuntap add dev fxp0 mode tap
    ifconfig fxp0 up promisc
    macchanger -A eth0
    brctl addif br-ext $eth
    brctl addif br-ext fxp0  
    echo "$eth -> fxp0"
    cat >> /tmp/$CONFIG <<EOF
      fxp0 {
        unit 0 {
          description "$eth-$ifdescr"
          family inet {
            address $myipmask;
          }
        }
      }
EOF
  else
    echo "$eth -> ge-0/0/$index"
    cat >> /tmp/$CONFIG <<EOF
      ge-0/0/$index {
        unit 0 {
          description "$eth-$ifdescr"
          family inet {
            address $myipmask;
          }
        }
      }
EOF
    index=$(($index + 1))
  fi
  ip addr flush dev $eth
done

cat >> /tmp/$CONFIG <<EOF
    }
    routing-options {
      static {
        route 0.0.0.0/0 next-hop $mygw;
      }
    }
  }
}
apply-groups docker-networking;
EOF

# find numanode to use based on PCI list.
# It will simply use the numanode of the last PCI.
# Using cards on different Nodes is not recommended 

for DEV in $@; do # ============= loop thru interfaces start
  PCI=${DEV%/*} 
  if [ "eth" != "${PCI:0:3}" ]; then
    CPU=$(cat /sys/class/pci_bus/${PCI%:*}/cpulistaffinity | cut -d'-' -f1 | cut -d',' -f1)
    NODE=$(numactl -H | grep "cpus: $CPU" | cut -d " " -f 2)
    if [ -z "$NUMAPREV" ]; then
      NUMAFIRST=$NODE
    fi
    if [ "$NODE" != "$NUMAFIRST" ]; then 
      echo "WARNING: Interface $PCI is on numa node $NODE, but first PCI interface is on node $NUMAFIRST"
    else
      echo "Interface $PCI is on node $NODE"
    fi
  fi
done
if [ ! -z "$NUMAFIRST" ]; then
  NUMANODE=$NUMAFIRST
fi

# append user provided config. Doing this after our initial settings ubove
# allows a user to overwrite our defaults, like host-name
if [ -f /u/$CONFIG ]; then
    cat /u/$CONFIG >> /tmp/$CONFIG
fi

mkdir /var/run/snabb
numactl --membind=$NUMANODE mount -t tmpfs -o rw,nosuid,nodev,noexec,relatime,size=4M tmpfs /var/run/snabb

brctl addbr br-int
ip addr add 128.0.0.16/8 dev br-int
ip link set up br-int
ip tuntap add dev em1 mode tap
ifconfig em1 up promisc
brctl addif br-int em1
brctl show

CFGDRIVE=/tmp/configdrive.qcow2
echo "Creating config drive $CFGDRIVE"
/create_config_drive.sh $CFGDRIVE /tmp/$CONFIG /u/$LICENSE 

/usr/sbin/rsyslogd

HDDIMAGE="/tmp/vmxhdd.img"
echo "Creating empty $HDDIMAGE for VCP ..."
qemu-img create -f qcow2 $HDDIMAGE 7G >/dev/null

echo "Building virtual interfaces and bridges for $@ ..."

INTNR=0	# added to each tap interface to make them unique
INTID="xe"

MACP=$(printf "02:%02X:%02X:%02X:%02X" $[RANDOM%256] $[RANDOM%256] $[RANDOM%256] $[RANDOM%256])

CPULIST=""  # collect cores given to PCIDEVS
ETHLIST=$(ifconfig|grep ^eth|grep -v eth0|cut -f1 -d' '|tr '\n' ' ')
LIST="$@ $ETHLIST"
echo "walking thru list of interfaces: $@ $ETHLIST ..."
for DEV in $LIST; do # ============= loop thru interfaces start

  # 0000:05:00.0/7 -> PCI=0000:05:00.0, CORE=7
  CORE=${DEV#*/}
  PCI=${DEV%/*} 
  INT="${INTID}${INTNR}"

  # create persistent mac address based on host-name in junos config file
  h=$(grep host-name /tmp/$CONFIG |md5sum)
  if [ "eth" == "${PCI:0:3}" ]; then
    macaddr="02:${h:0:2}:${h:2:2}:${h:4:2}:00:0$INTNR"
    CORE=""
    ifconfig $PCI mtu 9500
  else
    macaddr="02:${h:0:2}:${h:2:2}:${h:4:2}:${PCI:5:2}:0${PCI:11:1}"
    if [ "$CORE" -ge "0" ]; then
      echo "CORE=($CORE) PCI=($PCI)"
    else
      echo "FATAL configuration errror. Must specify core after PCI: $PCI/<core>"
      exit 1
    fi
    if [ -z "$CPULIST" ]; then
      CPULIST=$CORE
    else
      CPULIST="$CPULIST,$CORE"
    fi
  fi

  echo "PCI=$PCI CORE=$CORE CPULIST=$CPULIST"
  # add PCI to list
  PCIDEVS="$PCIDEVS $PCI"
  INTLIST="$INTLIST $INT"
  echo "$PCI/$CORE" > /tmp/pci_$INT
  echo "$macaddr" > /tmp/mac_$INT

  TAP="$INTID${INTNR}"    # -> tap/monitor interfaces xe0, xe1 etc
  ip tuntap add dev $TAP mode tap
  echo "created tap interface $TAP"

  NETDEVS="$NETDEVS -chardev socket,id=char$INTNR,path=./${INT}.socket,server \
        -netdev type=vhost-user,id=net$INTNR,chardev=char$INTNR \
        -device virtio-net-pci,netdev=net$INTNR,mac=$macaddr"

  INTNR=$(($INTNR + 1))
done # ===================================== loop thru interfaces done
echo "Done walking interface list"
if [ -z "$NETDEVS" ]; then
  echo "ERROR: no interfaces for vMX found"
  echo "NETDEVS=$NETDEVS"
  echo "INTERFACES=$@"
  echo "ETHLIST=$ETHLIST"
  echo "specify PCI interface address after the vMX bundle name "
  echo "or attach docker virtual networks before launching the container"
  exit 1
fi

QEMUVCPNUMA="numactl --membind=$NUMANODE"
if [ ! -z "$QEMUVCPCPUS" ]; then
  QEMUVCPNUMA="numactl --membind=$NUMANODE --physcpubind=$QEMUVCPCPUS"
fi

# calculate the cpu affinity mask excluding the ones for snabb
AVAIL_CORES=$(taskset -p $$|cut -d: -f2|cut -d' ' -f2)

echo "CPULIST=$CPULIST AVAIL_CORES=$AVAIL_CORES"

if [ ! -z "$CPULIST" ]; then 
  SNABB_AFFINITY=$(taskset -c $CPULIST /usr/bin/env bash -c 'taskset -p $$'|cut -d: -f2|cut -d' ' -f2)
  let AFFINITY_MASK="0x$AVAIL_CORES ^ 0x$SNABB_AFFINITY"
  AFFINITY_MASK=$(printf '%x\n' $AFFINITY_MASK)
  # Note: doesn't work with numactl: it will refuse to use a cpu that is masked out
  #echo "set cpu affinity mask $AFFINITY_MASK for everything but snabb"
  #taskset -p $AFFINITY_MASK $$
  echo "taskset -p $AFFINITY_MASK \$\$" >> /root/.bashrc
fi

BINDINGS=$(grep binding-table-file /tmp/$CONFIG | awk '{print $2}'|cut -d';' -f1)
if [ -f /u/$BINDINGS ]; then
  cp /u/$BINDINGS /tmp/
  BINDINGS=$(basename $BINDINGS)
else
  echo "WARNING: Binding table file $BINDINGS not found"
fi

if [ ! -z "$DEBUG" ]; then
   echo "Debug shell. Exit shell to continue"
   bash
   if [ $? -gt 0 ]; then
     exit
   fi
fi

# Launching snabb processes after we set excluded the cores
# from the scheduler
for INT in $INTLIST; do
  echo "Launching snabb on $INT"
  cd /tmp && numactl --membind=$NUMANODE /launch_snabb.sh $INT &
done


export PFE_SRC
sh /start_pfe.sh &

if [ ! -z "${JETUSER}${IDENTITY}" ]; then
  if [ -z "$JETUSER" ]; then
    cd /tmp && numactl --membind=$NUMANODE /launch_snabbvmx_manager.sh $MGMTIP $IDENTITY $BINDINGS &
  else
    cd /tmp && numactl --membind=$NUMANODE /launch_jetapp.sh $MGMTIP $JETUSER $JETPASS &
  fi
  # no longer required. JET daemon on Junos does the job now
  # cd /tmp && numactl --membind=$NUMANODE /launch_snabb_query.sh $MGMTIP $IDENTITY &
  cd /tmp && /launch_opserver.sh &
fi

cd /tmp
qemu-system-x86_64 -M pc --enable-kvm -cpu host -smp $VCPU -m $VCPMEM \
  -smbios type=0,vendor=Juniper \
  -smbios type=1,manufacturer=VMX,product=VM-vcp_vmx1-161-re-0,version=0.1.0 \
  -no-user-config \
  -no-shutdown \
  -drive if=ide,file=$VCPIMAGE -drive if=ide,file=$HDDIMAGE \
  -drive if=ide,file=$CFGDRIVE \
  -device cirrus-vga,id=video0,bus=pci.0,addr=0x2 \
  -netdev tap,id=tc0,ifname=fxp0,script=no,downscript=no \
  -device virtio-net-pci,netdev=tc0,mac=$mymac \
  -netdev tap,id=tc1,ifname=em1,script=no,downscript=no \
  -device virtio-net-pci,netdev=tc1 \
  -nographic || true

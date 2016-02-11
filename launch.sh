#!/bin/bash
#
qemu=/usr/local/bin/qemu-system-x86_64
snabb=/usr/local/bin/snabb

#---------------------------------------------------------------------------
function show_help {
  cat <<EOF
Usage:

docker run --name <name> --rm -v \$PWD:/u:ro \\
   --privileged -i -t marcelwiget/vmxlwaftr[:version] [-C <core>] \\
   -c <junos_config_file> -i identity [-l license_file] \\
   [-m <kbytes>] <image> <pci-address> [<pci-address> ...]

[:version]       Container version. Defaults to :latest

 -v \$PWD:/u:ro   Required to access a file in the current directory
                 docker is executed from (ro forces read-only access)
                 The file will be copied from this location

 -l  license_file to be loaded at startup (requires user snabbvmx with ssh
     private key given via option -i)

 -i  ssh private key for user snabbvmx 
     (required to access lwaftr config via netconf)

 -m  Specify the amount of memory for the vRE (default 8000kB)
 -V  number of vCPU's to assign to the vRR

 -C  pin snabb to a specific core(s) (in taskset -c format, defaults to 0)

 -d  Enable debug shell (launched before and after qemu runs)

<pci-address>    PCI Address of the Intel 825999 based 10GE port
                 Multiple ports can be specified, space separated

Example:
docker run --name lwaftr1 --rm --privileged -v \$PWD:/u:ro \\
  -i -t marcelwiget/vmxlwaftr -c lwaftr1.txt -i snabbvmx.key \\
  jinstall64-vrr-14.2R5.8-domestic.img 0000:05:00.0 0000:05:00.0

EOF
}

#---------------------------------------------------------------------------
function cleanup {

  set +e
  trap - EXIT SIGINT SIGTERM

  echo ""
  echo ""
  echo "vMX terminated."

  pkill snabb

  if [ ! -z "$PCIDEVS" ]; then
    echo "Giving 10G ports back to linux kernel"
    for PCI in $PCIDEVS; do
      if [ "$PCI" != "0000:00:00.0" ]; then
        echo -n "$PCI" > /sys/bus/pci/drivers/ixgbe/bind 2>/dev/null
      fi
    done
  fi
  exit 0

}
#---------------------------------------------------------------------------

function addif_to_bridge {
  ip link set master $1 dev $2
}

function create_tap_if {
  ip tuntap add dev $1 mode tap
  ip link set $1 up promisc on
}

function create_mgmt_bridge {
  if [ -z "`ifconfig docker0 >/dev/null 2>/dev/null && echo notfound`" ]; then
    # Running without --net=host. Create local bridge for MGMT and place
    # eth0 in it.
    bridge="br0"
    myip=`ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'`
    gateway=`ip -4 route list 0/0 |cut -d' ' -f3`
    ip addr flush dev eth0
    ip link add name $bridge type bridge
    ip link set up $bridge
    ip addr add $myip/16 dev br0
    route add default gw $gateway
    ip link set master $bridge dev eth0
  else
    bridge="docker0"
  fi
  echo $bridge
}

function mount_hugetables {
  >&2 echo "mounting hugepages ..."
  # mount hugetables, remove directory if this isn't possible due
  # to lack of privilege level. A check for the diretory is done further down
  mkdir /hugetlbfs && mount -t hugetlbfs none /hugetlbfs || rmdir /hugetlbfs

  # check that we are called with enough privileges and env variables set
  if [ ! -d "/hugetlbfs" ]; then
    >&2 echo "Can't access /hugetlbfs. Did you specify --privileged ?"
    exit 1
  fi

  hugepages=`cat /proc/sys/vm/nr_hugepages`
  if [ "0" -gt "$hugepages" ]; then
    >&2 echo "No hugepages found. Did you specify --privileged ?"
    exit 1
  fi
}

function get_mgmt_ip {
  # find IP address of em0 or fxp0 in given config
  grep --after-context=10 'em0 {\|fxp0 {' $1 | while IFS= read -r line || [[ -n "$line" ]]; do
      ipaddr="$(echo $line | grep address | awk -F "[ /]" '{print $2}')"
      if [ ! -z "$ipaddr" ]; then
        echo "$ipaddr"
        break
      fi
  done
}

function create_vmxhdd {
  >&2 echo "Creating empty vmxhdd.img for vRE ..."
  qemu-img create -f qcow2 /tmp/vmxhdd.img 2G >/dev/null
  echo "/tmp/vmxhdd.img"
}

function create_config_drive {
  >&2 echo "Creating config drive (metadata.img) ..."
  mkdir config_drive
  mkdir config_drive/boot
  mkdir config_drive/config
  mkdir config_drive/config/license
  cat > config_drive/boot/loader.conf <<EOF
vmchtype="vmx"
vm_retype="RE-VRR"
vm_instance="0"
EOF
  cp /u/$CONFIG config_drive/config/juniper.conf
  # placing license files on the config drive isn't supported yet
  # but it is assumed, this is how it will work.
  if [ -f *.lic ]; then
    for f in *.lic; do
      cp $f config_drive/config/license
    done
  fi
  cd config_drive
  tar zcf vmm-config.tgz *
  rm -rf boot config
  cd ..
  # Create our own metadrive image, so we can use a junos config file
  # 100MB should be enough.
  dd if=/dev/zero of=metadata.img bs=1M count=100 >/dev/null 2>&1
  mkfs.vfat metadata.img >/dev/null 
  mount -o loop metadata.img /mnt
  cp config_drive/vmm-config.tgz /mnt
  umount /mnt
}

function launch_debug_shell {
  echo "Launching shell to troubleshoot"
  set +e
  bash
  set -e
}

#==================================================================
# main()

echo "Juniper Networks vMX lwaftr Docker Container (unsupported prototype)"
echo ""
VCPMEM="8000"
CPUS="0"
VCPCPU="1"

while getopts "h?c:m:l:i:C:dV:" opt; do
  case "$opt" in
    h|\?)
      show_help
      exit 1
      ;;
    C)  CPUS=$OPTARG
      ;;
    V)  VCPCPU=$OPTARG
      ;;
    m)  VCPMEM=$OPTARG
      ;;
    c)  CONFIG=$OPTARG
      ;;
    l)  LICENSE=$OPTARG
      ;;
    i)  IDENTITY=$OPTARG
      ;;
    d)  DEBUG=$(($DEBUG + 1))
      ;;
  esac
done

shift "$((OPTIND-1))"

# first parameter is the vMX image
image=$1
shift

if [ ! -f "/u/$image" ]; then
  echo "Error: Can't find image $image"
  show_help
  exit 1
fi 

if [ ! -f "/u/$IDENTITY" ]; then
  echo "Error: Can't find private key file $identity"
  show_help
  exit 1
fi

cp /u/$image .
cp /u/$IDENTITY .
IDENTITY=$(basename $IDENTITY)
VCPIMAGE=$(basename $image)
HDDIMAGE=$(create_vmxhdd)
MGMTIP=$(get_mgmt_ip /u/$CONFIG)
$(mount_hugetables)
$(create_config_drive)
BRMGMT=$(create_mgmt_bridge)
# Create unique 4 digit ID used for this vMX in interface names
ID=$(printf '%02x%02x%02x' $[RANDOM%256] $[RANDOM%256] $[RANDOM%256])
# Create tap interfaces for mgmt
N=0
VCPMGMT="vcpm$ID$N"
N=$((N + 1))
$(create_tap_if $VCPMGMT)
$(addif_to_bridge $BRMGMT $VCPMGMT)

cat <<EOF

  vRE $VCPIMAGE with ${VCPMEM}kB
  mgmt interface $VCPMGMT IP $MGMTIP BRMGMT $BRMGMT
  config=$CONFIG license=$LICENSE identity=$IDENTITY
  CPUS for snabb: $CPUS

EOF

set -e	#  Exit immediately if a command exits with a non-zero status.
trap cleanup EXIT SIGINT SIGTERM

INTNR=1	# added to each tap interface to make them unique
INTID="em"

echo "Building virtual interfaces and bridges for $@ ..."

MACP=$(printf "02:%02X:%02X:%02X:%02X" $[RANDOM%256] $[RANDOM%256] $[RANDOM%256] $[RANDOM%256])

for DEV in $@; do # ============= loop thru interfaces start

  # add $DEV to list
  PCIDEVS="$PCIDEVS $DEV"
  macaddr=$MACP:$(printf '%02X'  $INTNR)
  INT="${INTID}${INTNR}"
  echo "$DEV" > pci_$INT
  echo "$macaddr" > mac_$INT

  NETDEVS="$NETDEVS -chardev socket,id=char$INTNR,path=./${INT}.socket,server \
   -netdev type=vhost-user,id=net$INTNR,chardev=char$INTNR \
   -device virtio-net-pci,netdev=net$INTNR,mac=$macaddr"

  if [ ! -z "$PREVINT" ]; then
    # launch snabb for every interface pair
    ./launch_snabb.sh $PREVINT $INT $CPUS &
    PREVINT=""
  else
    PREVINT=$INT
  fi

  INTNR=$(($INTNR + 1))

done # ===================================== loop thru interfaces done

# Check config for snabbvmx group entries. If there are any
# run its manager to create an intial set of configs for snabbvmx 
sx="\$(grep ' snabbvmx-' /u/$CONFIG)"
if [ ! -z "\$sx" ] && [ -f ./snabbvmx_manager.pl ]; then
    ./snabbvmx_manager.pl /u/$CONFIG
fi

if [ -f /u/$LICENSE ]; then
  cp /u/$LICENSE .
  LICENSE=$(basename $IDENTITY)
  ./add_license.sh $MGMTIP $IDENTITY $LICENSE &
fi

./launch_snabbvmx_manager.sh $MGMTIP $IDENTITY $CPUS &

if [ ! -z "$DEBUG" ]; then
  launch_debug_shell
fi

CMD="$qemu -M pc --enable-kvm -cpu host -smp $VCPCPU -m $VCPMEM -numa node,memdev=mem \
  -object memory-backend-file,id=mem,size=${VCPMEM}M,mem-path=/hugetlbfs,share=on \
  -drive if=ide,file=$VCPIMAGE -drive if=ide,file=$HDDIMAGE \
  -usb -usbdevice disk:format=raw:metadata.img \
  -device cirrus-vga,id=video0,bus=pci.0,addr=0x2 \
  -netdev tap,id=tc0,ifname=$VCPMGMT,script=no,downscript=no \
  -device e1000,netdev=tc0,mac=$MACP:99 $NETDEVS -nographic"

echo $CMD
$CMD

if [ ! -z "$DEBUG" ]; then
  launch_debug_shell
fi

exit  # this will call cleanup, thanks to trap set earlier (hopefully)

#!/bin/bash
# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.

#-----------------------------------------------------------
function extract_licenses {
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [ ! -z "$line" ]; then
      tmp="$(echo "$line" | cut -d' ' -f1)"
      if [ ! -z "$tmp" ]; then
        file=config_drive/config/license/${tmp}.lic
        >&2 echo "  writing license file $file ..."
        echo "$line" > $file
      else
        echo "$line" >> $file
      fi
    fi
  done < "$1"
}

#==================================================================
METADISK=$1
CONFIG=$2
LICENSE=$3

echo "METADISK=$METADISK CONFIG=$CONFIG LICENSE=$LICENSE"

echo "Creating config drive (configdrive.img) ..."
mkdir config_drive
mkdir config_drive/boot
mkdir config_drive/var
mkdir config_drive/var/db
mkdir config_drive/var/db/vmm
mkdir config_drive/var/db/vmm/etc
mkdir config_drive/var/db/vmm/scripts
mkdir config_drive/var/db/vmm/scripts/op
mkdir config_drive/var/db/vmm/scripts/snmp
mkdir config_drive/var/db/vmm/scripts/jet
mkdir config_drive/config
mkdir config_drive/config/license
cat > config_drive/boot/loader.conf <<EOF
vmchtype="vmx"
vm_retype="RE-VMX"
vm_instance="0"
EOF
if [ -f "$LICENSE" ]; then
  echo "extracting licenses from $LICENSE"
  $(extract_licenses $LICENSE)
fi

opfiles=$(ls /op/*slax)
slaxsnmpfiles=$(ls /snmp/*slax)
jetfiles=$(ls /jet/*py)
pysnmpfiles=$(ls /snmp/*py)
yangfiles=$(ls /yang/*.yang)

if [ ! -z "$opfiles" ]; then
  >&2 echo "SLAX/Python op files: $opfiles"
  cp $opfiles config_drive/var/db/vmm/scripts/op/
fi
if [ ! -z "$slaxsnmpfiles" ]; then
  >&2 echo "SLAX snmp files: $slaxsnmpfiles"
  cp $slaxsnmpfiles config_drive/var/db/vmm/scripts/snmp/
fi
if [ ! -z "$pysnmpfiles" ]; then
  >&2 echo "Python snmp files: $pysnmpfiles"
  cp $pysnmpfiles config_drive/var/db/vmm/scripts/snmp/
fi
if [ ! -z "$jetfiles" ]; then
  >&2 echo "Python JET files: $jetfiles"
  cp $jetfiles config_drive/var/db/vmm/scripts/jet/
fi
if [ ! -z "$yangfiles" ]; then
  yangcmd=""
  for file in $yangfiles; do
    if [ -f "$file" ]; then
      filebase=$(basename $file)
      grep "deviate " $file >/dev/null 2>&1
      if [ $? -eq 0 ]; then
        >&2 echo "YANG deviation file $file"
        yangcmd="$yangcmd -d /var/db/vmm/scripts/$filebase"
      else
        >&2 echo "YANG file $file"
        yangcmd="$yangcmd -m /var/db/vmm/scripts/$filebase"
      fi
      cp $file config_drive/var/db/vmm/scripts
    fi
  done

  yangrpc=$(ls /op/*py)
  if [ ! -z "$yangrpc" ]; then
    for file in $yangrpc; do
      filebase=$(basename $file)
      >&2 echo "YANG action script $file"
      yangcmd="$yangcmd -a /var/db/vmm/scripts/$filebase"
      chmod a+rx $file
      cp $file config_drive/var/db/vmm/scripts
    done
  fi
  cat > config_drive/var/db/vmm/etc/rc.vmm <<EOF
echo "------------> YANG import started"
ls /var/db/vmm/scripts
echo "/bin/sh /usr/libexec/ui/yang-pkg add -X -i lwaftr $yangcmd"
/bin/sh /usr/libexec/ui/yang-pkg add -X -i lwaftr $yangcmd
echo "------------> YANG import completed"
cp /var/etc/mosquitto.conf /var/etc/mosquitto.conf.orig
cp /var/db/vmm/mosquitto.conf.new /var/etc/mosquitto.conf
cp /var/db/vmm/scripts/op/* /var/db/scripts/op/
cp /var/db/vmm/scripts/snmp/* /var/db/scripts/snmp/
cp /var/db/vmm/scripts/jet/* /var/db/scripts/jet/
EOF
    chmod a+rx config_drive/var/db/vmm/etc/rc.vmm
    fi

    junospkg=$(ls /u/junos-*-x86-*tgz 2>/dev/null)
    if [ ! -z "$junospkg" ]; then
      filebase=$(basename $junospkg)
      cp $junospkg config_drive/var/db/vmm/
      PKG=$(echo $filebase|cut -d'-' -f1,2)
      if [ ! -z "$PKG" ]; then
        cat >> config_drive/var/db/vmm/etc/rc.vmm <<EOF
installed=\$(pkg info | grep $PKG)
if [ -z "\$installed" ]; then
  echo "Adding package $PKG (file $junospkg)"
  pkg add /var/db/vmm/$filebase
  reboot
fi
EOF
      fi
    fi
    cat > config_drive/var/db/vmm/mosquitto.conf.new <<EOF
bind_address 128.0.0.1
port 1883
junos_iri 1
user nobody
log_dest syslog
listener 1883
max_connections 20
max_queued_messages 0
max_inflight_messages 20
retry_interval 20
listener 41883 0.0.0.0 1
pid_file /var/run/mosquitto_jet.pid
EOF

junospkg=$(ls /u/junos-*-x86-*tgz 2>/dev/null)
if [ ! -z "$junospkg" ]; then
  echo "adding $junospkg"
  filebase=$(basename $junospkg)
  cp $junospkg config_drive/var/db/vmm/
  PKG=$(echo $filebase|cut -d'-' -f1,2)
  if [ ! -z "$PKG" ]; then
    cat >> config_drive/var/db/vmm/etc/rc.vmm <<EOF
installed=\$(pkg info | grep $PKG)
if [ -z "\$installed" ]; then
  echo "Adding package $PKG (file $junospkg)"
  pkg add /var/db/vmm/$filebase
  reboot
fi
EOF
    fi
  fi

echo "adding config file $CONFIG"
cp $CONFIG config_drive/config/juniper.conf

cd config_drive
tar zcf vmm-config.tgz *
rm -rf boot config var
cd ..

# Create our own metadrive image, so we can use a junos config file
# 50MB should be enough.
dd if=/dev/zero of=metadata.img  bs=1M count=50 >/dev/null 2>&1
mkfs.vfat metadata.img >/dev/null 
mount -o loop metadata.img /mnt
cp config_drive/vmm-config.tgz /mnt
umount /mnt
qemu-img convert -O qcow2 metadata.img $METADISK
rm metadata.img
ls -l $METADISK


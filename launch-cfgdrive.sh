#-----------------------------------------------------------
function create_config_drive {
  >&2 echo "Creating config drive (metadata.img) ..."
  mkdir config_drive
  mkdir config_drive/boot
  mkdir config_drive/var
  mkdir config_drive/var/db
  mkdir config_drive/var/db/vmm
  mkdir config_drive/var/db/vmm/etc
  mkdir config_drive/var/db/vmm/vmxlwaftr
  mkdir config_drive/var/db/vmm/vmxlwaftr/op
  mkdir config_drive/var/db/vmm/vmxlwaftr/snmp
  mkdir config_drive/var/db/vmm/vmxlwaftr/jet
  mkdir config_drive/config
  mkdir config_drive/config/license
  cat > config_drive/boot/loader.conf <<EOF
vmchtype="vmx"
vm_retype="RE-VMX"
vm_instance="0"
EOF
  if [ -f "/u/$LICENSE" ]; then
    >&2 echo "copying $LICENSE"
    $(extract_licenses /u/$LICENSE)
  fi
  if [ -z "${JETUSER}${IDENTITY}" ]; then
    >&2 echo "No identity. Not loading op/slax/yang files for lwaftr"
  else
    opfiles=$(ls /op/*slax)
    slaxsnmpfiles=$(ls /snmp/*slax)
    jetfiles=$(ls /jet/*py)
    pysnmpfiles=$(ls /snmp/*py)
    yangfiles=$(ls /yang/*.yang)
  fi
  if [ ! -z "$opfiles" ]; then
    >&2 echo "SLAX/Python op files: $opfiles"
    cp $opfiles config_drive/var/db/vmm/vmxlwaftr/op/
  fi
  if [ ! -z "$slaxsnmpfiles" ]; then
    >&2 echo "SLAX snmp files: $slaxsnmpfiles"
    cp $slaxsnmpfiles config_drive/var/db/vmm/vmxlwaftr/snmp/
  fi
  if [ ! -z "$pysnmpfiles" ]; then
    >&2 echo "Python snmp files: $pysnmpfiles"
    cp $pysnmpfiles config_drive/var/db/vmm/vmxlwaftr/snmp/
  fi
  if [ ! -z "$jetfiles" ]; then
    >&2 echo "Python JET files: $jetfiles"
    cp $jetfiles config_drive/var/db/vmm/vmxlwaftr/jet/
  fi
  if [ ! -z "$yangfiles" ]; then
     yangcmd=""
     for file in $yangfiles; do 
        if [ -f "$file" ]; then
           filebase=$(basename $file)
           grep "deviate " $file >/dev/null 2>&1
           if [ $? -eq 0 ]; then
            >&2 echo "YANG deviation file $file"
            yangcmd="$yangcmd -d /var/db/vmm/vmxlwaftr/$filebase"
           else
            >&2 echo "YANG file $file"
            yangcmd="$yangcmd -m /var/db/vmm/vmxlwaftr/$filebase"
           fi
           cp $file config_drive/var/db/vmm/vmxlwaftr
        fi
     done
     yangrpc=$(ls /op/*py)
     if [ ! -z "$yangrpc" ]; then
       for file in $yangrpc; do
           filebase=$(basename $file)
           >&2 echo "YANG action script $file"
           yangcmd="$yangcmd -a /var/db/vmm/vmxlwaftr/$filebase"
           chmod a+rx $file
           cp $file config_drive/var/db/vmm/vmxlwaftr
       done
     fi
    cat > config_drive/var/db/vmm/etc/rc.vmm <<EOF
echo "YANG import started"
ls /var/db/vmm/vmxlwaftr
echo "arg=$yangcmd"
/bin/sh /usr/libexec/ui/yang-pkg add -X -i lwaft $yangcmd
echo "YANG import completed"
cp /var/etc/mosquitto.conf /var/etc/mosquitto.conf.orig
cp /var/db/vmm/mosquitto.conf.new /var/etc/mosquitto.conf
cp /var/db/vmm/vmxlwaftr/op/* /var/db/scripts/op/
cp /var/db/vmm/vmxlwaftr/snmp/* /var/db/scripts/snmp/
cp /var/db/vmm/vmxlwaftr/jet/* /var/db/scripts/jet/
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
  cp /tmp/$CONFIG config_drive/config/juniper.conf
  cd config_drive
  tar zcf vmm-config.tgz *
  rm -rf boot config var
  cd ..
  # Create our own metadrive image, so we can use a junos config file
  # 100MB should be enough.
  dd if=/dev/zero of=metadata.img bs=1M count=100 >/dev/null 2>&1
  mkfs.vfat metadata.img >/dev/null 
  mount -o loop metadata.img /mnt
  cp config_drive/vmm-config.tgz /mnt
  umount /mnt
}

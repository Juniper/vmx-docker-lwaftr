#!/bin/ash

while :
do
  ping -c 3 lwaftr
  if [ 0 == $? ]; then
    break;
  fi
  echo "waiting for lwaftr to be reachable ..."
  sleep 5
done

dstmac=$(arp -na | awk '{print $4}')
srcmac=$(ifconfig eth0|grep HWaddr|awk '{print $5}')
echo "srcmac=$srcmac -> dstmac=$dstmac"
/usr/bin/snabb packetblaster lwaftr --src_mac $srcmac --dst_mac $dstmac --int eth0 $@

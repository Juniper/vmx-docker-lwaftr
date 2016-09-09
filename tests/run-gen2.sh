#!/usr/bin/env bash

SNABB=../build/snabb

PCIDEV=0000:05:00.1
INTERFACE=p1p2
RATE=0.1
CPU=7
if [ -z "$RATE" ]; then
  echo "Please specify rate in MPPS"
  exit 1
fi
FLOWS=60000
SMAC="02:02:02:02:02:02"
DMAC="02:42:df:27:05:00"
echo $INTERFACE at $PCIDEV has $MAC, running at $RATE gbps

CMD="sudo taskset -c $CPU $SNABB packetblaster lwaftr $OPT  --src_mac $SMAC --dst_mac $DMAC --b4 2001:db8::40,10.10.0.0,1024 --aftr 2001:db8:ffff::100 --count $FLOWS --rate $RATE --pci $PCIDEV # size --128  #--vlan 5"

echo $CMD

exec $CMD

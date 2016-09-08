#!/usr/bin/env bash

cp ../build/snabb .

PCIDEV=0000:05:00.1
INTERFACE=p1p2
RATE=3.1
CPU=7
if [ -z "$RATE" ]; then
  echo "Please specify rate in MPPS"
  exit 1
fi
FLOWS=64000
SMAC="02:02:02:02:02:02"
DMAC="02:42:df:27:05:00"
echo $INTERFACE at $PCIDEV has $MAC, running at $RATE gbps

CMD="sudo taskset -c $CPU ./snabb packetblaster lwaftr $OPT  --src_mac $SMAC --dst_mac $DMAC --b4 2a02:587:f710::40,10.10.0.0,1024 --aftr 2a02:587:f700::100 --count $FLOWS --rate $RATE --pci $PCIDEV # size --128  #--vlan 5"

echo $CMD

exec $CMD

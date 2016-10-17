#!/usr/bin/env bash

SNABB=../snabb/src/snabb

PCIDEV=0000:04:00.1
INTERFACE=ens6f1
RATE=3.1
CPU=4
if [ -z "$RATE" ]; then
  echo "Please specify rate in MPPS"
  exit 1
fi
FLOWS=60000
SMAC="02:02:02:02:02:02"
DMAC="02:b0:53:89:04:00"

echo $INTERFACE at $PCIDEV has $MAC, running at $RATE gbps

#CMD="sudo taskset -c $CPU $SNABB packetblaster lwaftr $OPT  --src_mac $SMAC --dst_mac $DMAC --b4 2001:db8::40,10.10.0.0,1024 --aftr 2001:db8:ffff::100 --count $FLOWS --rate $RATE --pci $PCIDEV"
CMD="sudo taskset -c $CPU $SNABB packetblaster lwaftr $OPT  --src_mac $SMAC --dst_mac $DMAC --b4 2001:db8::40,10.10.0.0,1024 --aftr 2001:db8:ffff::100 --count $FLOWS --rate $RATE --pci $PCIDEV --vlan 100"

echo $CMD

exec $CMD

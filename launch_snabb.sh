#!/usr/bin/env bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.
#
INT=$1

DEV=$(cat pci_$INT)
CORE=${DEV#*/}
PCI=${DEV%/*}
SLEEP=${INT:2:1}

if [ "eth" == "${PCI:0:3}" ]; then
   NODE=0
   NUMACTL=""
else
   CPU=$(cat /sys/class/pci_bus/${PCI%:*}/cpulistaffinity | cut -d'-' -f1 | cut -d',' -f1)
   NODE=$(numactl -H | grep "cpus: $CPU" | cut -d " " -f 2)
   NUMACTL="numactl --membind=$NODE --physcpubind=$CORE"
fi

while :
do
  # check if there is a snabb binary available in the mounted directory.
  # use that one if yes
  SNABB=/usr/local/bin/snabb
  if [ -f /u/snabb ]; then
    cp /u/snabb / 2>/dev/null
    SNABB=/snabb
  fi

  echo "launch snabbvmx for $INT on cpu $CORE (node $NODE) after $SLEEP seconds ..."
  CMD="$NUMACTL $SNABB snabbvmx lwaftr --conf snabbvmx-lwaftr-${INT}.cfg --id $INT --pci $PCI --mac `cat mac_$INT` --sock %s.socket"
  echo $CMD
  sleep $SLEEP
  touch /tmp/snabb_${INT}.log
  $CMD | tee /tmp/snabb_${INT}.log
  mosquitto_pub -h 128.0.0.1 -f /tmp/snabb_${INT}.log -t snabb/$INT
  sleep 4
done

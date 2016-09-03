#!/usr/bin/env bash
INT=$1

DEV=$(cat pci_$INT)
CORE=${DEV#*/}
PCI=${DEV%/*}
SLEEP=${INT:2:1}

if [ "eth" == "${PCI:0:3}" ]; then
   NODE=0
   NUMACTL="ip netns exec ns${INT}"
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
  $CMD
  sleep 4
done

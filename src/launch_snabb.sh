#!/usr/bin/env bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.
#
INT=$1

DEV=$(cat pci_$INT)
MAC=$(cat mac_$INT)
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
  # prepare test launch scripts for troubleshooting
  cat > test_snabb_lwaftr_${INT}.sh <<EOF
#!/bin/bash
echo "launching snabb lwaftr on-a-stick on PCI $PCI"
sudo usr/bin/snabb lwaftr run --conf snabbvmx-lwaftr-${INT}.conf --on-a-stick $PCI
EOF
  cp snabbvmx-lwaftr-${INT}.cfg test-snabbvmx-lwaftr-${INT}.cfg
  sed -i "s/cache_refresh_interval.*/cache_refresh_interval = 0,\n    next_hop_mac = \"02:02:02:02:02:02\",/" test-snabbvmx-lwaftr-${INT}.cfg
  cat > test_snabb_snabbvmx_${INT}.sh <<EOF
#!/bin/bash
echo "launching snabb snabbvmx on-a-stick on PCI $PCI"
sudo usr/bin/snabb snabbvmx lwaftr --conf test-snabbvmx-lwaftr-${INT}.cfg --id $INT --pci $PCI --mac $MAC
EOF
  chmod a+rx test_snabb_*sh

  echo "launch snabbvmx for $INT on cpu $CORE (node $NODE) after $SLEEP seconds ..."
  CMD="$NUMACTL /usr/bin/snabb snabbvmx lwaftr --conf snabbvmx-lwaftr-${INT}.cfg --id $INT --pci $PCI --mac $MAC --sock ext$INT --mirror tap${INT:2:1}"
  echo $CMD
  sleep $SLEEP
  touch /tmp/snabb_${INT}.log
  stdbuf -i0 -o0 -e0 $CMD | tee /tmp/snabb_${INT}.log
  mosquitto_pub -h 128.0.0.1 -f /tmp/snabb_${INT}.log -t snabb/$INT
  sleep 4
done

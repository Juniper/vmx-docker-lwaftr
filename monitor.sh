#!/usr/bin/env bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

a=0
b=0
c=0

PID=$(ps ax|grep snabbvmx-lwaftr|grep xe0|awk '{print $1}')
(./top.sh xe0 | grep Discards) &
(snabb top $PID | grep us) &

while true
do
date
x=`cat /proc/interrupts | grep TLB | awk '{print $19 " " $20 " " $21}'`
set -- $x
tlb19=$(($a - $1))
tlb20=$(($b - $2))
tlb21=$(($c - $3))
echo "$x $tlb19 $tlb20 $tlb21"
a=$1
b=$2
c=$3

sleep 1
done

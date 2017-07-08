#!/bin/bash
# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.

# Hack to fix a pending network ordering issue in Docker
# https://github.com/docker/compose/issues/4645
# We use docker insepct of our very own container to learn the expected network
# order by grabbing the MAC addresses, except eth0, which is always correct.
# Then we swap the ethX interfaces as needed

# get ordered list of MAC addresses, but skip the first empty one and eth0
MACS=$(docker inspect $HOSTNAME|grep MacAddr|awk '{print $2}' | cut -d'"' -f2| tail -n +3)

echo $MACS
index=1
for mac in $MACS; do
  FROM=$(ifconfig | grep $mac | cut -d' ' -f1)
  TO="eth$index"
  if [ "$FROM" == "$TO" ]; then
    echo "$mac $FROM == $TO"
  else
    echo "$mac $FROM -> $TO"
    ifconfig $FROM down
    ifconfig $TO down
    ip link set $FROM name peth
    ip link set $TO name $FROM
    ip link set peth name $TO
    ifconfig $FROM up
    ifconfig $TO up
  fi
  index=$(($index + 1))
done

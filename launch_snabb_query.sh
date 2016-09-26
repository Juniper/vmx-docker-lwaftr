#!/bin/bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

MGMTIP=$1
IDENTITY=$2

echo "$0: launching snabbvmx query $MGMTIP $IDENTITY"

if [ -z "$IDENTITY" ]; then
  echo "Usage: $0 management-ip-address identity.key"
  exit 1
fi

while :
do
  SNABB=/usr/local/bin/snabb
  if [ -f /snabb ]; then
    SNABB=/snabb
  fi
  $SNABB snabbvmx query > /tmp/stats.xml
  scp -o StrictHostKeyChecking=no -i /u/$IDENTITY /tmp/stats.xml snabbvmx@$MGMTIP:/tmp
  sleep 5
done

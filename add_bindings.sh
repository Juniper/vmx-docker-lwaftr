#!/usr/bin/env bash

MGMTIP=$1
IDENTITY=$2
BINDINGS=$3

if [ ! -f "$BINDINGS" ]; then
  echo "no binding file found at $BINDINGS"
  echo "Usage: $0 mgmt-ip-adress identity binding-file"
  exit 1
fi

# With IPv6 addresses, use square brackets for scp
if [[ $MGMTIP == *":"* ]]; then
  MGMTIPSCP="[$MGMTIP]"
else
  MGMTIPSCP=$MGMTIP
fi

# vRE might not be up for a while, so keep trying to upload the license file ...
while true; do
  scp -o StrictHostKeyChecking=no -i $IDENTITY $BINDINGS snabbvmx@$MGMTIPSCP:/var/db/scripts/commit/
  if [ $? == 0 ]; then
    echo "transfer successful"
    break;
  fi
  echo "binding upload failed ($?), sleeping 5 seconds ..."
  sleep 5
done

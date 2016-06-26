#!/usr/bin/env bash
MGMTIP=$1
JETUSER=$2
JETPASS=$3

if [ -z "$JETPASS" ]; then
  echo "Usage: $0 management-ip-address jetuser jetpass"
  exit 1
fi

while :
do
  python /jetapp/src/main.py --host $MGMTIP --user $JETUSER --password $JETPASS
  sleep 5
done

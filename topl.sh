#!/usr/bin/env bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

PORT="${1:-xe0}"
while :
do
  SNABB_PID=$(ps ax |grep $PORT | grep snabbvmx|grep pci|awk '{print $1}'|tail -1)
  if [ ! -z "$SNABB_PID" ]; then
    snabb top $SNABB_PID
  fi
  echo "waiting for snabb on $PORT ..."
  sleep 1
done

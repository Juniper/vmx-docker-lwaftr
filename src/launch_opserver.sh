#!/bin/bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

echo "$0: Launching jetapp op server"
while :
do
  python /jetapp/op/opserver.py
  echo "jetapp op terminated. Restarting in 5 seconds ..."
  sleep 5
done

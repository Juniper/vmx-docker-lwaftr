#!/bin/bash
# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.

BINDINGS=$1

echo "$0: launching snabbvmx manager $BINDINGS"

if [ -f "$BINDINGS" ]; then
  /add_bindings.sh $BINDINGS 
fi

while :
do
  /snabbvmx_manager.pl
  echo "snabbvmx_manager.pl terminated. Restarting in 5 seconds ..."
  sleep 5
done
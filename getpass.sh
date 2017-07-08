#!/bin/bash
# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.
#
# simple script to extract root passwords from vmx log file

list=$(docker ps --format '{{.Names}}' | grep vmx)
for vmx in $list; do
  pass=$(docker logs $vmx | grep 'password to')
  echo "$vmx: $pass"
done

#!/usr/bin/env bash
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

SNABB_PID=$(ps ax |grep snabbvmx-lwaftr|awk '{print $1}')
QEMU_PID=$(ps ax |grep qemu-system|awk '{print $1}')
ps -o pid,psr,comm $SNABB_PID $QEMU_PID

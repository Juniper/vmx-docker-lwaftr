#!/usr/bin/env bash

SNABB_PID=$(ps ax |grep snabbvmx-lwaftr|awk '{print $1}')
QEMU_PID=$(ps ax |grep qemu-system|awk '{print $1}')
ps -o pid,psr,comm $SNABB_PID $QEMU_PID

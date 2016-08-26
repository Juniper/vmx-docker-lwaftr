#!/bin/bash

NAME="lwaftr2"
CFG="lwaftr2.txt"
VMX="vmx-bundle-16.1R1.8.tgz"
#CONTAINER="marcelwiget/vmxlwaftr:v0.8"
CONTAINER="vmxlwaftr:v0.9"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
#INTERFACES="0000:05:00.0 0000:05:00.0"
LICENSE="license-eval.txt"
INTERFACES="tap/6 tap/7"

docker rm $NAME 2>/dev/null
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -i $IDENTITY -l $LICENSE -c $CFG $VMX $INTERFACES
docker rm $NAME

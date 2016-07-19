#!/bin/bash

NAME="lwaftr1"
CFG="lwaftr1.txt"
#VMX="vmx-bundle-16.1-20160528_ib_16_1_jdi.2.tgz"
#VMX="vmx-bundle-16.1-20160514_ib_16_1_jdi.1.tgz"
VMX="vmx-bundle-16.1R1.8.tgz"
#CONTAINER="marcelwiget/vmxlwaftr:v0.8"
CONTAINER="vmxlwaftr:v0.9"
IDENTITY="snabbvmx.key"
#INTERFACES="0000:05:00.0 0000:05:00.0"
LICENSE="license-eval.txt"
INTERFACES="tap/6 tap/7"

docker rm $NAME 2>/dev/null
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -i $IDENTITY -l $LICENSE -c $CFG $VMX $INTERFACES
docker rm $NAME

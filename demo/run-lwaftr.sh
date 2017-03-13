#!/bin/bash

NAME="lwaftr"
CFG="lwaftr.txt"
VMX="vmx-bundle-16.1R3.10.tgz"
CONTAINER="vmx-docker-lwaftr:v1.1.21"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
INTERFACES="0000:03:00.0/3 0000:04:00.0/4"
LICENSE="license-eval.txt"

docker rm $NAME 2>/dev/null
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $VMX $INTERFACES
docker rm $NAME

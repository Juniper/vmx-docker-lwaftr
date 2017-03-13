#!/bin/bash

NAME="lwb4sim"
CFG="lwb4sim.txt"
VMX="vmx-bundle-16.1R3.10.tgz"
#VMX="vmx-bundle-17.1R1.8.tgz"
CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
INTERFACES="0000:03:00.1/6 0000:04:00.1/5"
LICENSE="license-eval.txt"

docker rm $NAME 2>/dev/null
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $VMX $INTERFACES
docker rm $NAME

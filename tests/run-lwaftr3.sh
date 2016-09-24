#!/bin/bash

NAME="lwaftr3"
CFG="lwaftr3.txt"
#VMX="vmx-bundle-16.1R2.11.tgz"
VMX="vmx-bundle-16.1-20160915.0.tgz"
CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
INTERFACES="0000:05:00.0/6"
LICENSE="license-eval.txt"

docker rm $NAME 2>/dev/null
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $VMX $INTERFACES
docker rm $NAME

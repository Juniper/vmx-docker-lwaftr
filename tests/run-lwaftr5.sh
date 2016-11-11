#!/bin/bash

NAME="lwaftr5"
CFG="lwaftr5.txt"
VMX="vmx-bundle-16.1R3.10.tgz"
CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
INTERFACES="0000:03:00.0/10 0000:04:00.0/12"
LICENSE="license-eval-private.txt"

docker rm $NAME 2>/dev/null
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $VMX $INTERFACES
docker rm $NAME

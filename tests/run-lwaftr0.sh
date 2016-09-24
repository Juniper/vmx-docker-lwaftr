#!/bin/bash

NAME="lwaftr0"
CFG="lwaftr0.txt"
VMX="vmx-bundle-16.1R2.11.tgz"
CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
LICENSE="license-eval.txt"
INTERFACES=""

docker rm $NAME 2>/dev/null
docker create --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $1 $VMX $INTERFACES
#docker network connect net1 $NAME
#docker network connect net2 $NAME
docker start -a -i $NAME
docker rm $NAME

#!/bin/bash

NAME="lwaftr4"
NET1="net1-lwaftr4"
NET2="net2-lwaftr4"
NET3="net3-lwaftr4"
NET4="net4-lwaftr4"
docker network create $NET1
docker network create $NET2
docker network create $NET3
docker network create $NET4
if [ ! -e binding_table.txt ]; then
  cp binding_table_60k.txt binding_table.txt
fi

CFG="lwaftr4.txt"
VMX="vmx-bundle-16.1R2.11.tgz"

CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
LICENSE="license-eval.txt"
INTERFACES=""

docker rm $NAME 2>/dev/null
docker create --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $1 $VMX $INTERFACES
docker network connect $NET1 $NAME
docker network connect $NET2 $NAME
docker network connect $NET3 $NAME
docker network connect $NET4 $NAME
docker start -a -i $NAME
docker rm $NAME

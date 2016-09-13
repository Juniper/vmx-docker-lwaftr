#!/bin/bash

NAME="lwaftr1"
NET="net-lwaftr1"
CFG="lwaftr1.txt"
VMX="vmx-bundle-16.1R1.7.tgz"
CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
LICENSE="license-eval.txt"
INTERFACES=""

NETID=$(docker network inspect --format "{{ .Id }}" $NET 2>/dev/null)
if [ -z "$NETID" ]; then
  echo "docker network $NET doesn't exist. Please run ./create-lwaftr1-testbed.sh first"
  exit 1
fi

docker rm $NAME 2>/dev/null
docker create --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER -I $IDENTITY -l $LICENSE -c $CFG $1 $VMX $INTERFACES
docker network connect $NET $NAME
docker start -a -i $NAME
docker rm $NAME

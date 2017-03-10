#!/bin/bash

NAME="lwaftr1"
NET="net-lwaftr1"

CFG="lwaftr1.txt"
#VMX="vmx-bundle-16.1R3.10.tgz"
VMX="vmx-bundle-16.1R4.7.tgz"
#VMX="vmx-bundle-17.1R1.8.tgz"

CONTAINER="$(cat ../VERSION)"
IDENTITY="snabbvmx.key"
chmod 400 $IDENTITY
LICENSE="license-eval.txt"
INTERFACES=""

DUP=$(docker ps -f name=${NAME} --format "{{ .Names }}" | grep "^${NAME}$")
if [ -n "$DUP" ]; then
  echo "antother container with same name $NAME exists. Kindly choose another NAME"
  exit 1
fi

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

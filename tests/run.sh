#!/bin/bash
CONTAINER="vmxlwaftr:v0.9"
NAME="lwaftr-help"
echo "Launching $CONTAINER without arguments to print out help"
docker rm $NAME >/dev/null 2>&1
docker run --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER
docker rm $NAME >/dev/null 2>&1

#!/bin/bash
NAME="b4cpe1"
CONTAINER="b4cpe:v0.1"

IP="193.5.1.3"
IP6="fd00:4600::1001"
GW6="fd00:4600::1"
PORTRANGE="1024-2047"
AFTR="fd00:4600:8888::1"

docker create --name $NAME -ti --privileged -v $PWD:/u:ro $CONTAINER $IP $PORTRANGE $GW6 $AFTR
#docker network create net1 2>/dev/null
docker network connect --ip6 $IP6 net1 $NAME
docker start -a -i $NAME 
docker rm $NAME

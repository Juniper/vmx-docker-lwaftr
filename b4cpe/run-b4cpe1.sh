#!/bin/bash
NAME="b4cpe1"
CONTAINER="b4cpe:v0.1"

NET="net1"
IP="193.5.1.2"
IP6="fd00:4600::1001"
GW6="fd00:4600::1"
PORTRANGE="1024-2047"
AFTR="fd00:4600:8888::2"

docker run --name $NAME -ti --privileged --network=$NET --ip6=$IP6 -v $PWD:/u:ro $CONTAINER $IP $PORTRANGE $GW6 $AFTR
docker rm $NAME

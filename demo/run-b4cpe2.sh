#!/bin/bash
NAME="b4cpe2"
CONTAINER="b4cpe:v0.1"

NET="net-lwaftr1"
IP="193.5.1.2"
IP6="fd00:4600::1002"
GW6="fd00:4600::1"
PORTRANGE="2048-3071"
AFTR="fd00:4600:8888::2"

docker run --name $NAME -ti --privileged --network=$NET --ip6=$IP6 -v $PWD:/u:ro $CONTAINER $IP $PORTRANGE $GW6 $AFTR
docker rm $NAME

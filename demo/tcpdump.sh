#!/bin/bash
CONTAINER=$1
if [ -z "$CONTAINER" ]; then
  echo "Usage: $0 <container>"
  exit 1
fi
echo $CONTAINER
docker exec -ti $CONTAINER tcpdump -n -s 1500 -i eth0 proto 4

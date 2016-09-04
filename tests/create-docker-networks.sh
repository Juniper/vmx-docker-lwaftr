#!/bin/bash
docker network rm net1 net2 2>/dev/null
docker network create --subnet=172.20.0.0/24 --gateway=172.20.0.1 \
  --aux-address a=172.20.0.2 --ip-range=172.20.0.0/24 \
  --ipv6 --subnet=fd00:4600::/64 --aux-address a=fd00:4600::2 --gateway=fd00:4600::1 net1

# add 2nd subnet to net1. Docker network doesn't support multiple IP networks yet on bridge
# so we do it manually here.
BRIDGE="br-$(docker network inspect --format "{{ .Id }}" net1 | cut -b 1-12)"
sudo ip -6 addr add fd00:4600:1110::1/64 dev $BRIDGE
sudo route -6 add fd00:4600:8888::1/32 gw fd00:4600:1110::2

docker network create --subnet=172.20.2.0/23 --gateway=172.20.2.1 \
  --aux-address a=172.20.2.2 --ip-range=172.20.3.0/24 \
  --ipv6 --subnet=fd00:4601::/64 --aux-address a=fd00:4601::2 --gateway=fd00:4601::1 net2
BRIDGE="br-$(docker network inspect --format "{{ .Id }}" net2 | cut -b 1-12)"
sudo ip -6 addr add fd00:4600:1111::1/64 dev $BRIDGE

docker network ls

echo "adding route for 193.5.1/0 to vMX at 172.20.0.2"
sudo route add -net 193.5.1.0/24 gw 172.20.0.2

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

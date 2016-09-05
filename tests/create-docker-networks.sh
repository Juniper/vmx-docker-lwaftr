#!/bin/bash
docker network rm net1 net2 2>/dev/null
docker network create --subnet=172.20.0.0/24 --gateway=172.20.0.1 \
  --aux-address a=172.20.0.2 --ip-range=172.20.0.0/24 \
  --ipv6 --subnet=fd00:4600::/64 --aux-address a=fd00:4600::2 --gateway=fd00:4600::1 net1

# add 2nd subnet to net1. Docker network doesn't support multiple IP networks yet on bridge
# so we do it manually here.
sleep 5
BRIDGE="br-$(docker network inspect --format "{{ .Id }}" net1 | cut -b 1-12)"
sudo ip -6 addr add fd00:4600:1110::1/64 dev $BRIDGE
sudo route -6 add fd00:4600:8888::2/128 gw fd00:4600:1110::2
sudo route -6 add fd00:4600:8888::3/128 gw fd00:4600:1110::3
sudo route -6 add fd00:4600:8888::4/128 gw fd00:4600:1110::4
sudo route -6 add fd00:4600:8888::5/128 gw fd00:4600:1110::5
sudo route -6 add fd00:4600:8888::6/128 gw fd00:4600:1110::6
sudo route -6 add fd00:4600:8888::7/128 gw fd00:4600:1110::7
sudo route -6 add fd00:4600:8888::8/128 gw fd00:4600:1110::8
sudo route -6 add fd00:4600:8888::9/128 gw fd00:4600:1110::9

docker network create --subnet=172.20.2.0/23 --gateway=172.20.2.1 \
  --aux-address a=172.20.2.2 --ip-range=172.20.3.0/24 \
  --ipv6 --subnet=fd00:4601::/64 --aux-address a=fd00:4601::2 --gateway=fd00:4601::1 net2
BRIDGE="br-$(docker network inspect --format "{{ .Id }}" net2 | cut -b 1-12)"
sudo ip -6 addr add fd00:4600:1111::1/64 dev $BRIDGE

docker network ls

echo "adding static ip subnet routes (/29) for 193.5.1.0 to vMX's"
sudo route add -net 193.5.1.0/29 gw 172.20.0.2
sudo route add -net 193.5.1.8/29 gw 172.20.0.3
sudo route add -net 193.5.1.16/29 gw 172.20.0.4
sudo route add -net 193.5.1.24/29 gw 172.20.0.5
sudo route add -net 193.5.1.32/29 gw 172.20.0.6
sudo route add -net 193.5.1.40/29 gw 172.20.0.7
sudo route add -net 193.5.1.48/29 gw 172.20.0.8
sudo route add -net 193.5.1.56/29 gw 172.20.0.9

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

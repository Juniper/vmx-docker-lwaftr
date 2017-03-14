#!/bin/bash

# Network parameters that connects the B4 client to the vMX via the linux docker network

NET="net-lwaftr1"

NET4="172.20.0.0/24"
GWIP4="172.20.0.1"
VMXIP4="172.20.0.2"
VMXIP6="fd00:4600:1110::2"

NET6="fd00:4600::/64"
GWIP6="fd00:4600::1"

AFTR="fd00:4600:8888::2"
PUBLIC="193.5.1.0/24"

echo -n "checking if docker network $NET already exists ... "
NETID=$(docker network inspect --format "{{ .Id }}" $NET 2>/dev/null) 
if [ ! -z "$NETID" ]; then
  echo ""
  echo "$NET already exists ($NETID)."
  echo "Delete it first with 'docker network rm $NET' if you need to have it recreated"
  exit 1
fi
echo "ok"

echo "need sudo privileges:"
sudo pwd

echo -n "creating network $NET ..."
NETID=$(docker network create --subnet=$NET4 --aux-address a=$VMXIP4 \
  --gateway=$GWIP4 --ipv6 --subnet=$NET6 --gateway=$GWIP6 $NET)
echo "ok"

echo -n "adding IPv6 network for lwaftr1 ... "
BRIDGE="br-$(docker network inspect --format "{{ .Id }}" $NET | cut -b 1-12)"
echo -n " on $BRIDGE "
sudo ip -6 addr add fd00:4600:1110::1/64 dev $BRIDGE
echo "ok"

echo -n "adding static route to AFTR $AFTR via gw $VMXIP6 ... "
sudo route -6 add $AFTR/128 gw $VMXIP6
echo "ok"

echo -n "adding static route to $PUBLIC via $VMXIP4 ... " 
sudo route add -net $PUBLIC gw $VMXIP4
echo "ok"

gwdev=$(ip -4 route list 0/0 |cut -d' ' -f5)
echo -n "Adding SNAT masquerading via interface $gwdev"
sudo iptables -t nat --flush
sudo iptables -t nat -A POSTROUTING -o $gwdev -j MASQUERADE
echo " all set."


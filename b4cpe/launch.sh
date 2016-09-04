#!/bin/bash
cat /VERSION
ifconfig eth1 >/dev/null 2>&1
if [ $? -gt 0 ]; then
  echo "Need virtual network on eth1"
  exit 1
fi

IP=$1
PORTRANGE=$2
GW6=$3
AFTR=$4

# we ignore the assigned IPv6 address and use our own. Lets save the orig one
MYIP6=$(ifconfig eth1|grep inet6|grep -v fe80|awk '{print $3}'|cut -f1 -d/)
echo "MY IPv6 address is $MYIP6"
ip -6 tunnel add mytun mode ipip6 remote $AFTR local $MYIP6 dev eth1
ip link set dev mytun up
ip -6 addr add $MYIP6 dev eth1
ip -6 addr add $MYIP6 dev mytun
ip route del default
ip route add default dev mytun
route -6 del default
route -6 add default gw $GW6

iptables -t nat --flush
iptables -t nat -A POSTROUTING -p tcp -o mytun -j SNAT --to $IP:$PORTRANGE
iptables -t nat -A POSTROUTING -p udp -o mytun -j SNAT --to $IP:$PORTRANGE
iptables -t nat -A POSTROUTING -p icmp -o mytun -j SNAT --to $IP:$PORTRANGE

echo "IP=$IP PORTRANGE=$PORTRANGE MYIP6=$MYIP6 AFTR=$AFTR"
bash

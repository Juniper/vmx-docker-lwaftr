#!/bin/bash
echo ""
cat /VERSION | xargs
echo ""

IP=$1
PORTRANGE=$2
GW6=$3
AFTR=$4
CONTAINER=$(head -1 /VERSION)

if [ -z "$AFTR" ]; then
  cat <<EOF

  Usage: 
  #!/bin/bash
  CONTAINER="$CONTAINER"
  NAME="myname"
  NET="net1"
  IP="193.5.1.3"
  IP6="fd00:4600::1001"
  GW6="fd00:4600::1"
  PORTRANGE="1024-2047"
  AFTR="fd00:4600:8888::1"

  docker run --name \$NAME -ti --privileged --network=\$NET --ip6=\$IP6 -v \$PWD:/u:ro \$CONTAINER \$IP \$PORTRANGE \$GW6 \$AFTR
  docker rm $NAME
EOF
  exit 1
fi

# we ignore the assigned IPv6 address and use our own. Lets save the orig one
MYIP6=$(ifconfig eth0|grep inet6|grep -v fe80|awk '{print $3}'|cut -f1 -d/)
ip -6 tunnel add mytun mode ipip6 remote $AFTR local $MYIP6 dev eth0
ip link set dev mytun up
ip route del default
ip route add default dev mytun
route -6 add default gw $GW6

iptables -t nat --flush
iptables -t nat -A POSTROUTING -p tcp -o mytun -j SNAT --to $IP:$PORTRANGE
iptables -t nat -A POSTROUTING -p udp -o mytun -j SNAT --to $IP:$PORTRANGE
iptables -t nat -A POSTROUTING -p icmp -o mytun -j SNAT --to $IP:$PORTRANGE

echo "nameserver 8.8.8.8" > /etc/resolv.conf

echo "Welcome to the B4 client"
echo ""
echo "My IPv6 address on eth0 is $MYIP6"
echo "My IPv6 remote tunnel endpoint (AFTR) is $AFTR"
echo "My assigned IPv4 address and port range is $IP $PORTRANGE"
#echo "IP=$IP PORTRANGE=$PORTRANGE MYIP6=$MYIP6 AFTR=$AFTR"
export IP PORTRANGE MYIP6 AFTR CONTAINER
echo
iptables -t nat --list POSTROUTING
echo
bash

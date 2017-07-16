#!/bin/ash



ifconfig eth0:1 1.1.1.1 netmask 255.255.255.0

ethtool -K eth0 tx off
ethtool -K eth0:1 tx off

echo "removing default route"
ip route del default

while :
do
  ping -c 3 lwaftr
  if [ 0 == $? ]; then
    break;
  fi
  echo "waiting for lwaftr to be reachable ..."
  sleep 5
done

gw=$(dig +short lwaftr)

echo "adding default route via lwaftr ($gw)"
ip route add default via $gw

cat > /var/www/localhost/htdocs/index.html <<EOF

$HOSTNAME - container server running 
Using lwaftr at $gw as default gateway.

EOF

lighttpd -D -f /etc/lighttpd/lighttpd.conf

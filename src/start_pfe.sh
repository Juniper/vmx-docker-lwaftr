#!/bin/sh
# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.
#

PFE_SRC=/usr/share/pfe

# Start broadcasting Gratuitous ARP and ping
#  required to keep VCP arp table up-to-date
arping -q -A -I br-int 128.0.0.16  2>&1 > /dev/null &
ping -i 3 -rnq -I br-int 128.0.0.1 2>&1 > /dev/null &

# Wait for VM to start/boot
echo -n "Waiting for VCP to boot... "
start=$(date +"%s")
while ! ping -nqc1 -I br-int -W 1 128.0.0.1 2>&1 > /dev/null; do
  sleep 1
done
end=$(date +"%s")
echo "Done [$(($end - $start))s]"

# patch riot to allow macvlan interfaces too
echo "patching riot.tgz ..."
cd /tmp
rcp 128.0.0.1:/usr/share/pfe/riot_lnx.tgz .
tar zxf riot_lnx.tgz
patch -p0 < /riot.patch
tar zcf riot_lnx.tgz riot
rsh 128.0.0.1 mv /usr/share/pfe/riot_lnx.tgz /usr/share/pfe/riot_lnx.tgz.orig
rcp riot_lnx.tgz 128.0.0.1:/usr/share/pfe/
cd /
echo "done"

rcp 128.0.0.1:${PFE_SRC}/mpcsd_lnx ${PFE_SRC}/mpcsd
rcp 128.0.0.1:${PFE_SRC}/mpcsd_lnx.sha1 ${PFE_SRC}/

echo "Starting mpcsd"
${PFE_SRC}/mpcsd 0 2986 1 -N -L

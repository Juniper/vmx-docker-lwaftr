# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

FROM ubuntu:14.04
MAINTAINER Marcel Wiget

# install tools required in the running container
RUN apt-get -o Acquire::ForceIPv4=true update \
  && apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends \
  net-tools iproute2 dosfstools tcpdump bridge-utils numactl genisoimage \
  libaio1 libspice-server1 libncurses5 openssh-client libjson-xs-perl \
  python-twisted mosquitto-clients python-setuptools

# fix usr/sbin/tcpdump by moving it into /sbin: 
#  error while loading shared libraries: libcrypto.so.1.0.0: 
#  cannot open shared object file: Permission denied
RUN mv /usr/sbin/tcpdump /sbin/

# dumb-init
COPY dumb-init/dumb-init /usr/bin/

COPY qemu-v2.4.1-snabb.tgz /
RUN tar zxf /qemu-v*-snabb.tgz -C /usr/local/

# python-tools
COPY python-tools.tgz /
RUN tar zxf python-tools.tgz && rm python-tools.tgz 

# Snabb
COPY snabb/src/snabb /usr/local/bin/

RUN mkdir /yang /jetapp /jetapp/op /utils /op /snmp /jet

COPY yang/ietf-inet-types.yang yang/ietf-yang-types.yang \
  yang/ietf-softwire.yang \
  jetapp/yang/op/junos-extension.yang jetapp/yang/op/junos-extension-odl.yang \
  jetapp/yang/op/rpc-get-lwaftr.yang jetapp/yang/op/rpc-get-lwaftr-statistics.yang \
  jetapp/yang/op/rpc-monitor-lwaftr.yang \
  yang/jnx-aug-softwire.yang yang/jnx-softwire-dev.yang yang/

COPY jetapp/src/op/__init__.py jetapp/src/op/opglobals.py jetapp/src/op/opserver.py /jetapp/op/

COPY slax/lwaftr.slax \
  jetapp/yang/op/rpc_get_lwaftr_state.py \
  jetapp/yang/op/rpc_monitor_lwaftr.py \
  jetapp/yang/op/rpc_get_lwaftr_statistics.py op/

COPY jetapp/yang/op/rpc-jet.py jet/

COPY snmp/snmp_lwaftr.slax snmp/lw4over6.py snmp/

COPY launch.sh launch_snabb.sh top.sh topl.sh README.md VERSION \
  launch_jetapp.sh launch_opserver.sh \
  launch_snabbvmx_manager.sh snabbvmx_manager.pl show_affinity.sh \
  monitor.sh add_bindings.sh launch_snabb_query.sh /

RUN date >> /VERSION

EXPOSE 8700 

ENTRYPOINT ["/usr/bin/dumb-init", "/launch.sh"]
CMD ["-h"]

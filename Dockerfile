# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.

FROM ubuntu:14.04
LABEL maintainer Juniper Networks

RUN export DEBIAN_FRONTEND=noninteractive \
  && dpkg --add-architecture i386 \
  && apt-get update && apt-get install -y -q qemu-kvm qemu-utils dosfstools pwgen \
    openssh-client bridge-utils ethtool bsdmainutils wget ca-certificates patch \
    rsh-client psmisc libpcap0.8 iputils-arping pciutils tcpdump macchanger \
    python-twisted mosquitto-clients python-setuptools numactl libjson-xs-perl \
    libc6:i386 libncurses5:i386 libstdc++6:i386 \
    --no-install-recommends \
  && echo "dash dash/sh boolean false" | debconf-set-selections \
  && dpkg-reconfigure dash \
  && ln -sf /usr/lib/x86_64-linux-gnu/libpcap.so.1.5.3 /usr/lib/x86_64-linux-gnu/libpcap.so.1 \
  && mv /usr/sbin/tcpdump /sbin/ \
  && mkdir -p /home/pfe/junos /home/pfe/riot /usr/share/pfe /etc/riot \
  && mkdir -p /var/pfe /var/riot /var/jnx /var/tmp/vmx \
  && mkdir /yang /jetapp /jetapp/op /utils /op /snmp /jet

# Required for docker client, so we can fix the network interface ordering issue,
# documented in https://github.com/docker/compose/issues/4645

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y -q --no-install-recommends \
    apt-transport-https ca-certificates curl software-properties-common \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
    && add-apt-repository \
      "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs)  stable" \
    && apt-get update && apt-get -y -q --no-install-recommends install docker-ce

# dumb-init
COPY dumb-init/dumb-init /usr/bin/

# python-tools
COPY python-tools.tgz /
RUN tar zxf python-tools.tgz && rm python-tools.tgz 

# Snabb
COPY snabb/src/snabb /usr/local/bin/

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
  launch_jetapp.sh launch_opserver.sh create_config_drive.sh \
  launch_snabbvmx_manager.sh snabbvmx_manager.pl show_affinity.sh \
  add_bindings.sh \
  riot.patch start_pfe.sh fix_network_order.sh /

RUN chmod a+rx /*.sh

RUN date >> /VERSION

VOLUME /u /var/run/docker.sock

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/usr/bin/dumb-init", "/launch.sh"]

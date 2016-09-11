FROM ubuntu:14.04.5
MAINTAINER Marcel Wiget

# install tools required in the running container
RUN apt-get -o Acquire::ForceIPv4=true update \
  && apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends \
  net-tools iproute2 dosfstools tcpdump bridge-utils numactl genisoimage \
  libaio1 libspice-server1 libncurses5 openssh-client libjson-xs-perl \
  mosquitto-clients

# fix usr/sbin/tcpdump by moving it into /sbin: 
#  error while loading shared libraries: libcrypto.so.1.0.0: 
#  cannot open shared object file: Permission denied
RUN mv /usr/sbin/tcpdump /sbin/

# dumb-init
COPY dumb-init/dumb-init /usr/bin/

# Snabb
COPY build/snabb /usr/local/bin/

COPY build/qemu-v2.4.1-snabb.tgz /
RUN tar zxf /qemu-v*-snabb.tgz -C /usr/local/

RUN mkdir /yang /slax /snmp

COPY yang/ietf-inet-types.yang yang/ietf-yang-types.yang \
  yang/ietf-softwire.yang \
  yang/jnx-softwire.yang yang/jnx-softwire-dev.yang yang/

COPY slax/lwaftr.slax slax/
COPY snmp/snmp_lwaftr.slax snmp/

COPY launch.sh launch_snabb.sh top.sh topl.sh README.md VERSION \
  launch_snabbvmx_manager.sh snabbvmx_manager.pl show_affinity.sh nexthop.sh \
  monitor.sh add_bindings.sh launch_snabb_query.sh /

RUN date >> /VERSION

EXPOSE 8700 

ENTRYPOINT ["/usr/bin/dumb-init", "/launch.sh"]
CMD ["-h"]

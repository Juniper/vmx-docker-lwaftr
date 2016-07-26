FROM ubuntu:14.04.4
MAINTAINER Marcel Wiget

# install tools required in the running container
RUN apt-get -o Acquire::ForceIPv4=true update \
  && apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends \
  net-tools iproute2 dosfstools tcpdump bridge-utils numactl genisoimage \
  libaio1 libspice-server1 libncurses5 openssh-client libjson-xs-perl

# fix usr/sbin/tcpdump by moving it into /sbin: 
#  error while loading shared libraries: libcrypto.so.1.0.0: 
#  cannot open shared object file: Permission denied
RUN mv /usr/sbin/tcpdump /sbin/

COPY build/snabb /usr/local/bin/

COPY build/qemu-v2.4.0-snabb.tgz /
#COPY build/qemu-v2.5.1.1-snabb.tgz /
RUN tar zxf /qemu-v*-snabb.tgz -C /usr/local/


COPY launch.sh launch_snabb.sh top.sh topl.sh README.md VERSION \
  launch_snabbvmx_manager.sh snabbvmx_manager.pl add_bindings.sh \
  yang/ietf-inet-types.yang  yang/ietf-softwire.yang \
  yang/jnx-softwire.yang yang/jnx-softwire-dev.yang \
  show_affinity.sh nexthop.sh monitor.sh /

RUN date >> /VERSION

EXPOSE 8700 

ENTRYPOINT ["/launch.sh"]

CMD ["-h"]

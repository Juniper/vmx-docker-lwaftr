FROM ubuntu:14.04.4
MAINTAINER Marcel Wiget

# install tools required in the running container
RUN apt-get -o Acquire::ForceIPv4=true update \
  && apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends \
  net-tools iproute2 dosfstools tcpdump bridge-utils numactl genisoimage \
  libaio1 libspice-server1 libncurses5 

# fix usr/sbin/tcpdump by moving it into /sbin: 
#  error while loading shared libraries: libcrypto.so.1.0.0: 
#  cannot open shared object file: Permission denied
RUN mv /usr/sbin/tcpdump /sbin/

COPY build/snabb /usr/local/bin/

COPY build/qemu-v2.4.0-snabb.tgz /
#COPY build/qemu-v2.5.1.1-snabb.tgz /
RUN tar zxf /qemu-v*-snabb.tgz -C /usr/local/

# install JET
COPY jet-1.tar.gz /
RUN apt-get -o Acquire::ForceIPv4=true \
  install -y --no-install-recommends build-essential libffi-dev \
  python-pip python-dev libssl-dev libxml2-dev libxslt1-dev \
  && pip install cryptography==1.2.1 && pip install junos-eznc \
  && pip install twisted && pip install jinja2 \
  && pip install /jet-1.tar.gz && rm /jet-1.tar.gz \
  && apt-get purge -y python-dev libssl-dev build-essential && apt-get autoremove -y

COPY launch.sh launch_snabb.sh launch_jetapp.sh top.sh topl.sh README.md VERSION \
   jetapp.tgz show_affinity.sh nexthop.sh /

#COPY launch.sh README.md snabbvmx_manager.pl add_bindings.sh nexthop.sh \
#  launch_snabbvmx_manager.sh launch_snabb.sh show_affinity.sh top.sh topl.sh \
#  launch_snabbvmx_jet.sh SnabbVmxJET.tar.gz /

# install JETapp
RUN tar zxf /jetapp.tgz 2>/dev/null && rm /jetapp.tgz

RUN date >> /VERSION

EXPOSE 8700 

ENTRYPOINT ["/launch.sh"]

CMD ["-h"]

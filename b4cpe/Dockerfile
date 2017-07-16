FROM ubuntu:14.04
LABEL maintainer Juniper Networks

# install tools required in the running container
RUN apt-get update && apt-get install -y --no-install-recommends ethtool \
  net-tools iproute2 tcpdump tcpreplay iptables wget lynx python-pip \
  && pip install scapy

# fix usr/sbin/tcpdump by moving it into /sbin: 
#  error while loading shared libraries: libcrypto.so.1.0.0: 
#  cannot open shared object file: Permission denied
RUN mv /usr/sbin/tcpdump /sbin/

COPY VERSION launch.sh /

RUN date >> /VERSION

ENTRYPOINT ["/launch.sh"]

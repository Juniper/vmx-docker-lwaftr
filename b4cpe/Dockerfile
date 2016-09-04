FROM ubuntu:14.04.5
MAINTAINER Marcel Wiget

# install tools required in the running container
RUN apt-get -o Acquire::ForceIPv4=true update \
  && apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends \
  net-tools iproute2 tcpdump tcpreplay iptables

# fix usr/sbin/tcpdump by moving it into /sbin: 
#  error while loading shared libraries: libcrypto.so.1.0.0: 
#  cannot open shared object file: Permission denied
RUN mv /usr/sbin/tcpdump /sbin/

#COPY dumb-init snabb /usr/bin/
COPY VERSION launch.sh /

RUN date >> /VERSION

ENTRYPOINT ["/launch.sh"]
CMD [""]

FROM alpine:3.6
LABEL maintainer Juniper Networks

RUN apk --no-cache add iptables tcpdump bind-tools lighttpd ethtool

COPY launch.sh /
RUN chmod a+rx /launch.sh

ENTRYPOINT ["/launch.sh"]

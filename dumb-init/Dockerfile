FROM ubuntu:14.04.4
MAINTAINER Marcel Wiget

COPY 99force-ipv4 /etc/apt/apt.conf.d/

RUN apt-get update && apt-get install -y --no-install-recommends build-essential git musl-tools

COPY build.sh /

CMD [ "/build.sh"]

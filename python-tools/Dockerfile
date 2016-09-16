FROM ubuntu:14.04.5
MAINTAINER Marcel Wiget

COPY 99force-ipv4 /etc/apt/apt.conf.d/

RUN apt-get update && apt-get install -y --no-install-recommends build-essential git python-pip python-dev

RUN mkdir /build && pip install --root /build thrift paho-mqtt Jinja2
COPY build.sh /

CMD [ "/build.sh"]

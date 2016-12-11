FROM ubuntu:14.04
MAINTAINER Marcel Wiget

RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential git 
   
RUN apt-get install -y --no-install-recommends ca-certificates \
   libqtcore4 libusbredirhost1 qtcore4-l10n spice-client-glib-usb-acl-helper \
   libffi-dev sshpass openssh-client rsync psmisc glib-2.0 libglib2.0-dev \
   libaio-dev libcap-dev libattr1-dev libpixman-1-dev libncurses5 \
   libncurses5-dev libspice-server1 libtool musl-tools python-pip python-dev

RUN mkdir /build && pip install --root /build thrift paho-mqtt Jinja2

COPY build.sh /

CMD [ "/build.sh"]

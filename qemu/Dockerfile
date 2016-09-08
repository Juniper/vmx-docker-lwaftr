FROM ubuntu:14.04.5
MAINTAINER Marcel Wiget

COPY 99force-ipv4 /etc/apt/apt.conf.d/

RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential git ca-certificates libqtcore4 libusbredirhost1 \
   qtcore4-l10n spice-client-glib-usb-acl-helper libffi-dev \
   sshpass openssh-client rsync psmisc glib-2.0 libglib2.0-dev \
   libaio-dev libcap-dev libattr1-dev libpixman-1-dev libncurses5 \
   libncurses5-dev libspice-server1 libtool 

COPY build.sh /

CMD [ "/build.sh"]

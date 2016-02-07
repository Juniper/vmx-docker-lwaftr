FROM ubuntu:14.04.3
MAINTAINER Marcel Wiget

# Install enough packages to compile snabb and qemu
RUN apt-get update
RUN apt-get install -y --no-install-recommends net-tools iproute2 dosfstools

# Download and compile snabb and qemu, then cleanup
RUN apt-get install -y --no-install-recommends build-essential git ca-certificates \
  libqtcore4 libusbredirhost1 qtcore4-l10n spice-client-glib-usb-acl-helper \
  sshpass openssh-client rsync psmisc glib-2.0 libglib2.0-dev libaio-dev libcap-dev \
  libattr1-dev libpixman-1-dev libncurses5 libncurses5-dev libspice-server1 \
  && git clone -b vmx_rambutan https://github.com/mwiget/snabbswitch.git \
  && cd snabbswitch && make -j && make install && make clean && cd .. \
  && git clone -b v2.4.0-snabb --depth 50 https://github.com/SnabbCo/qemu \
  && cd qemu && ./configure --target-list=x86_64-softmmu --disable-sdl && make -j \
  && make install \
  && apt-get purge -y build-essential git ca-certificates libncurses5-dev glib-2.0 \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* /snabbswitch /qemu

COPY launch.sh README.md snabbvmx_manager.pl add_license.sh \
  launch_snabbvmx_manager.sh launch_snabb.sh /

ENTRYPOINT ["/launch.sh"]

CMD ["vmx"]

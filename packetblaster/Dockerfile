# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.

FROM alpine:3.6
MAINTAINER Marcel Wiget

RUN apk add --no-cache libgcc

RUN apk add --no-cache --virtual build-dependencies \
  gcc git ca-certificates musl-dev make linux-headers findutils \
  && git clone --recursive https://github.com/snabbco/snabb.git \
  && cd snabb && make && cp src/snabb /usr/bin/ && cd .. \
  && rm -rf snabb && apk del build-dependencies

COPY launch.sh /
RUN chmod a+rx /*sh

ENTRYPOINT ["/launch.sh"]

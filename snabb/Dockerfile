# Copyright (c) 2017, Juniper Networks, Inc.
# All rights reserved.

FROM alpine:3.6
MAINTAINER Marcel Wiget

RUN apk add --no-cache libgcc tcpdump bind-tools

ENV SNABB_REPO https://github.com/mwiget/snabb.git
ENV SNABB_BRANCH criot

RUN apk add --no-cache --virtual build-dependencies \
  gcc git ca-certificates musl-dev make linux-headers findutils \
  && git clone -b $SNABB_BRANCH --recursive $SNABB_REPO \
  && cd snabb && make && cp src/snabb /usr/bin/ && cd .. \
  && rm -rf snabb && apk del build-dependencies

ENTRYPOINT ["/usr/bin/snabb"]

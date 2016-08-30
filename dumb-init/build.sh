#!/usr/bin/env bash
set +e
git config --global http.sslVerify false
git clone https://github.com/Yelp/dumb-init.git
cd dumb-init
CC=musl-gcc make
cp dumb-init /u

#!/usr/bin/env bash
set +e
mkdir /build
echo "copying source files ..."
cp -rp /u/* build/
cd build
echo "building snabb ..."
make -j
cp src/snabb /u/src
md5sum src/snabb /u/src/snabb

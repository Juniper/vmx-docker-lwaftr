#!/usr/bin/env bash
set +e
mkdir /build
echo "copying source files ..."
cp -rp /u/* build/
cd build
echo "building qemu ..."
./configure --target-list=x86_64-softmmu --disable-sdl --prefix=/ship
make -j
make install
TARFILE=qemu-v$(cat VERSION)-snabb.tgz
cd /ship
tar zcf /u/$TARFILE .
ls -l /u/$TARFILE

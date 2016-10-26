#!/usr/bin/env bash
set +e

# JET
echo ""
echo "-------------------------"
echo "building jet-python ..."
cd /u/jet-python && python setup.py install --root=/build --single-version-externally-managed

echo ""
echo "-------------------------"
echo "building python-tools ..."
cd /build
tar zcvf /u/python-tools.tgz *

echo "-------------------------"
echo "building snabb ..."
cd /u/snabb
make
md5sum src/snabb
echo "done"

echo ""
echo "-------------------------"
echo "building qemu ..."
cd /u/qemu
patch -p1 --forward < /u/qemu-snabb.diff
./configure --target-list=x86_64-softmmu --disable-sdl --prefix=/ship
make -j
make install
TARFILE=qemu-v$(cat VERSION)-snabb.tgz
cd /ship
tar zcf /u/$TARFILE .
echo "$TARFILE built."
echo "done."

echo ""
echo "-------------------------"
echo "building dumb-init ..."
cd /u/dumb-init
CC=musl-gcc make
echo "done."



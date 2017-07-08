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


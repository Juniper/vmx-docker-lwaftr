#!/usr/bin/env bash
while :
do
  python /jetapp/main.py
  echo "jetapp terminated. Restarting in 5 seconds ..."
  sleep 5
done

#!/bin/bash
echo "$0: Launching jetapp server"
while :
do
  python /jetapp/main.py
  echo "jetapp terminated. Restarting in 5 seconds ..."
  sleep 5
done

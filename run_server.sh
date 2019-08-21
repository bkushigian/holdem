#!/bin/bash

PORT=65432
HOST="all"

if [ "$1" == "-h" ] || [ "$1" == "--help" ]
then
  echo "usage: ./run_server.sh [PORT]"
  echo "    PORT is the port to listen to (default 65432)"
  exit 1
fi

if [ ! -z "$1"]
then
  PORT="$1"
fi

cd src
python3 run_server.py $PORT $HOST

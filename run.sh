#!/bin/bash
PORT=65432
HOST="167.71.182.40"

if [ "$1" == "-h" ] || [ "$1" == "--help" ]
then
  echo "usage: ./run.sh [HOST [PORT]]"
  echo "    HOST is either the IP of the host server or 'local' or 'localhost' for a local match"
  echo "    PORT is the port to connect to (default 65432)"
  exit 1
fi

if [ "$1" == "local" ]  || [ "$1" == "localhost" ]
then
  HOST="localhost"
elif [ ! -z "$1" ]
then
  HOST="$1"
fi

if [ ! -z "$2"]
then
  PORT="$2"
fi
cd src
python3 run_client.py $PORT $HOST

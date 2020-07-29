#!/bin/bash

# Build and install libsbox first, located in ./libsbox/
# Before running, specify INVOKER_NAME if there are many invokers

export DATA_DIR=$PWD/../data

sudo libsboxd start &
sudo -E python3 invoker.py

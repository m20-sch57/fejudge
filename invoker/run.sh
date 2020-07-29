#!/bin/bash

export DATA_DIR=$PWD/../data

sudo libsboxd start &
python3 invoker.py

#!/bin/bash

export DATA_DIR=$PWD/../data

libsboxd start &
python3 invoker.py

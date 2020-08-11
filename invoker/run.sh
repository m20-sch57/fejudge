#!/bin/bash

export STORAGE_DIR=$PWD/../storage

libsboxd start &
python3 run.py

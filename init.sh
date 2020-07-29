#!/bin/bash

if ! [ -d 'data' ]; then
    mkdir data
fi

if ! [ -d 'logs' ]; then
    mkdir logs
fi

python3 init.py

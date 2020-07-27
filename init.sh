#!/bin/bash

if ! [ -d 'logs' ]; then
    mkdir logs
fi

python3 init.py

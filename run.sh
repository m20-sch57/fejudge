#!/bin/bash

export DATA_DIR=$PWD/data
export FLASK_DEBUG=0

nats-server --log logs/nats.log &
python3 run.py

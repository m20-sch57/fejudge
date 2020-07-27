#!/bin/bash

# Before running, specify MAIL_USERNAME and MAIL_PASSWORD of smtp server

export DATA_DIR=$PWD/data
export FLASK_DEBUG=0

nats-server --log logs/nats.log &
python3 run.py

#!/bin/bash

# Before running, specify MAIL_USERNAME and MAIL_PASSWORD of smtp server

export FLASK_APP=app
export FLASK_ENV=development
export FLASK_DEBUG=false
export DATA_DIR=$PWD/data

if ! [ -d 'logs' ]; then
    mkdir logs
fi

nats-server -l logs/nats.log &
python3 -m flask run --host=0.0.0.0 --port=3013

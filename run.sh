#!/bin/bash

export FLASK_APP=app
export DATA_DIR=$PWD/data
export SANDBOX_DIR=$PWD/sandbox

if ! [ -d 'tmp' ]; then
    mkdir tmp
fi

sudo libsboxd start &
nats-streaming-server &

if ! [ -f 'tmp/invoker.pid' ]; then
    sudo -E python3 tools/invoker/invoker.py \&> tmp/invoker.log &
    echo $! > 'tmp/invoker.pid'
else
    echo 'tmp/invoker.pid exists, failed to start'
fi
if ! [ -f 'tmp/packagebuilder.pid' ]; then
    sudo -E python3 tools/packagebuilder/packagebuilder.py \&> tmp/packagebuilder.log &
    echo $! > 'tmp/packagebuilder.pid'
else
    echo 'tmp/packagebuilder.pid exists, failed to start'
fi

python3 run.py

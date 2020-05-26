#!/bin/bash

export FLASK_APP=app
export DATA_DIR=./data
export SANDBOX_DIR=./sandbox

if ! [ -d 'tmp' ]; then
    mkdir tmp
fi

sudo libsboxd start &

if ! [ -f 'tmp/invoker.pid' ]; then
    sudo -E python3 tools/invoker/invoker.py \&> tmp/invoker.log &
    echo $! > 'tmp/invoker.pid'
else
    echo 'tmp/invoker.pid exists, delete it or start manually!'
fi
if ! [ -f 'tmp/packagebuilder.pid' ]; then
    sudo -E python3 tools/packagebuilder/builder.py \&> tmp/packagebuilder.log &
    echo $! > 'tmp/packagebuilder.pid'
else
    echo 'tmp/packagebuilder.pid exists, delete it or start manually!'
fi

python3 run.py

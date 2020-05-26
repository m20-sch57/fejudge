#!/bin/bash

if [ -f 'tmp/invoker.pid' ]; then
    kill `cat tmp/invoker.pid`
    rm 'tmp/invoker.pid'
    echo 'Killed invoker'
fi
if [ -f 'tmp/packagebuilder.pid' ]; then
    kill `cat tmp/packagebuilder.pid`
    rm 'tmp/packagebuilder.pid'
    echo 'Killed package builder'
fi

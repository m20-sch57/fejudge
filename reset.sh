#!/bin/bash

if ! [ -d 'data' ]; then
    mkdir 'data'
fi

rm -rf data/*
mkdir data/download
mkdir data/download/submissions
mkdir data/upload
mkdir data/upload/problems
mkdir data/problems

python3 reset.py

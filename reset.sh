#!/bin/bash

if ! [ -d 'storage' ]; then
    mkdir 'storage'
fi

rm -rf storage/*
mkdir storage/download
mkdir storage/download/submissions
mkdir storage/upload
mkdir storage/upload/problems
mkdir storage/problems

python3 reset.py

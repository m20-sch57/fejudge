#!/bin/bash

python3 -m flask db upgrade
python3 reset.py
python3 run.py

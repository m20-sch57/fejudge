#!/bin/bash

# Usage:
# `sudo ./setup_nfs_server.sh`

# Before running, do the following:

# 1. `sudo apt update && sudo apt install nfs-kernel-server` (if it is not installed)
# 2. `sudo nano /etc/exports`, and add all IP addresses of invokers and main server (app)
# 3. `sudo exportfs –a`

sudo chown -R nobody:nogroup data/
sudo service rpcbind restart
sudo service nfs-kernel-server start

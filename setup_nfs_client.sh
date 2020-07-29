#!/bin/bash

# Usage:
# `sudo ./setup_nfs_client.sh <DATA_REMOTE_PATH>`,
# where <DATA_REMOTE_PATH> is a remote path to data directory on NFS server, for example `57.57.57.57:/Fejudge/data`.

# Before running, do the following:

# 1. `sudo apt update && sudo apt install nfs-common` (if it is not installed)

if ! [ -d data ]; then
    mkdir data
fi

sudo mount $1 data/

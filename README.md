# Fejudge

Fair electronic judge

## About Fejudge

Fejudge is a contest management system, created for automatic solution evaluation. It was inspired by other grading systems, such as Codeforces, Ejudge and CMS.

With help of [libsbox](https://github.com/Forestryks/libsbox), Fejudge is designed to become faster than other systems while evaluating submissions - evaluation on 50 tests of a correct solution to problem A+B takes 1-2 secs.

To become familiar with Fejudge, visit http://m20-sch57.site:3113/, where the test build is located. There are some easy problems which you can solve and submit solutions in order to check perfomance of Fejudge (or to enjoy its nice user interface).

Fejudge supports problem packages built on [polygon](http://polygon.codeforces.com).

## Getting started

These instructions will guide you through the installation process of Fejudge.

### Prerequisites

- linux kernel version 5 or higher
- cgroup v1 heirarchy mounted in /sys/fs/cgroup
- C++ 17 compiler, with `std::filesystem` support
- CMake version 3.10 or higher
- Python 3.6 or higher, see `requirements.txt`

### Setting up NFS server

1. Download `nfs-kernel-server` package
2. Create storage folder and set correct permissions to it
```
mkdir storage
sudo chown nobody:nogroup storage/
```
2. Open file `/etc/exports` and share this folder with all other clients
3. Export it
```
sudo exportfs -a
```
4. Start `rpcbind` and `nfs-kernel-server` services
```
sudo service rpcbind start
sudo service nfs-kernel-server start
```

### Setting up NFS clients (main server and invokers)

1. Download `nfs-common` package
2. Mount remote storage folder
```
mkdir storage
sudo mount <STORAGE_REMOTE_FOLDER> storage/
```
`STORAGE_REMOTE_FOLDER` is a remote path to storage directory on NFS server, for example `57.57.57.57:/Fejudge/storage`.

### Setting up PostgreSQL server

1. Download `postgresql` package
2. Start `postgresql` service
```
sudo service postgresql start
```
3. Create database `database.db` and user `postgres` with password `postgres`
```
sudo -u postgres createuser postgres
sudo -u postgres createdb database.db
sudo -u postgres psql
psql=# alter user postgres with encrypted password 'postgres';
```
If you use another login and password, then specify `POSTGRES_USER` and `POSTGRES_PASSWORD` variables at each client.

### Setting up NATS server

1. Download and install [NATS Server](https://docs.nats.io/nats-server/installation)
2. Run it by typing `nats-server`

### Setting up main server

1. Upgrade database and initialize defaults
```
flask db upgrade
./reset.sh
```
2. Run main server
```
export POSTGRES_URL=<...>:5432
export NATS_URL=<...>:4222
export MAIL_USERNAME=<...>
export MAIL_PASSWORD=<...>
./run.sh
```
Your email will be used to send informational letters.

### Setting up invoker

1. Compile and install [libsbox](https://github.com/Forestryks/libsbox), located in `./invoker/libsbox`
2. Run invoker
```
cd invoker/
export POSTGRES_URL=<...>:5432
export SOCKETIO_URL=<...>:3113
export NATS_URL=<...>:4222
sudo -E ./run.sh
```
If you want to run multiple invokers on a single machine, specify `INVOKER_NAME` before running
```
export INVOKER_NAME=<UNIQUE_ID>
```

### Run in docker

To start in docker, run `docker-compose build && docker-compose up` in the project directory.

## Documentation

TODO

## Authors

- **Fedor Kuyanov**([@kuyanov](https://github.com/kuyanov))
- **Andrei Odintsov** ([@Forestryks](https://github.com/Forestryks))

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



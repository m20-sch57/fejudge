# Fejudge

Fair electronic judge

## About Fejudge

Fejudge is contest management system, created for automatic solution evaluation.

## Getting started

These instructions will guide you through the installation process of Fejudge.

### Prerequisites

- linux kernel version 5 or higher
- cgroup v1 heirarchy mounted in /sys/fs/cgroup
- C++ 17 compiler, with `std::filesystem` support
- CMake version 3.10 or higher
- OpenJDK Runtime environment 11.0.4
- Python 3.4 or higher with `flask`, `flask_avatars`, `flask_sqlalchemy`, `flask_migrate`, `flask_login`, `flask_wtf`, `flask_mail`, `kafka-python`, `StringGenerator`

### Installing

1. Run main server
```
python3 run.py
```
2. Download kafka binaries from [here](https://kafka.apache.org/downloads) and extract it
3. Run kafka servers
```
./run_kafka.sh <PathToKafkaBinaries>
```
4. Go to directory ```Fejudge/tools/libsbox/daemon``` , set up [libsbox](https://github.com/Forestryks/libsbox) and run it
5. Go to invoker directory, assign environment variable ```DATA_DIR``` to where data is located. Then run invoker in order to judge solutions
```
cd Fejudge/tools/invoker
export DATA_DIR=../../data
sudo python3 invoker.py
```

To start in docker, run ```docker-compose up``` in the project directory.

## Documentation

TODO

## Authors

- **Fedor Kuyanov**([@kuyanov](https://github.com/kuyanov))
- **Andrei Odintsov** ([@Forestryks](https://github.com/Forestryks))

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



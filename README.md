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
- Python 3.4 or higher with `flask`, `flask_avatars`, `flask_sqlalchemy`, `flask_migrate`, `flask_login`, `kafka`

### Installing

1. Download kafka binaries from [here](https://kafka.apache.org/downloads) and extract it
2. Set up [libsbox](https://github.com/Forestryks/libsbox)
3. Run kafka servers
```
./run_kafka.sh <PathToKafkaBinaries>
```
4. Run main server
```
python3 run.py
```
5. Run invoker in order to judge solutions
```
sudo python3 invoker.py
```

## Documentation

TODO

## Authors

- **Fedor Kuyanov**([@kuyanov](https://github.com/kuyanov))
- **Andrei Odintsov** ([@Forestryks](https://github.com/Forestryks))

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details



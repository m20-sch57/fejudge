# Fejudge

Fair electronic judge

## About Fejudge

Fejudge is a contest management system, created for automatic solution evaluation. It was inspired by other grading systems, such as Codeforces, Ejudge and CMS.

With help of [libsbox](https://github.com/Forestryks/libsbox), Fejudge is designed to become faster than other systems while evaluating submissions - evaluation on 50 tests of a correct solution to problem A+B takes 1-2 secs.

To become familiar with Fejudge, visit http://m20-sch57.site:3013/, where the test build is located. There are some easy problems which you can solve and submit solutions in order to check perfomance of Fejudge (or to enjoy its nice user interface).

Currently Fejudge supports problem packages which were built on [polygon](http://polygon.codeforces.com), and only full problem scoring (without subtasks).

## Getting started

These instructions will guide you through the installation process of Fejudge.

### Prerequisites

- linux kernel version 5 or higher
- cgroup v1 heirarchy mounted in /sys/fs/cgroup
- C++ 17 compiler, with `std::filesystem` support
- CMake version 3.10 or higher
- OpenJDK Runtime environment 11.0.4
- Python 3.6 or higher with `Flask`, `Flask-Avatars`, `Flask-Login`, `Flask-Mail`, `Flask-Migrate`, `Flask-SQLAlchemy`, `Flask-WTF`, `WTForms-Components`, `SQLAlchemy`, `nats-python`, `StringGenerator` - see `requirements.txt`

### Installing

1. Download and install [NATS Streaming](https://nats.io/download/nats-io/nats-streaming-server)
2. Compile and install [libsbox](https://github.com/Forestryks/libsbox), located in `./invoker/libsbox`
3. Create and upgrade database
```
flask db upgrade
```
4. Initialize all data
```
python3 init.py
```
5. Run main script
```
./run.sh
```
6. Run invoker
```
cd invoker/
sudo -E ./run.sh
```

<!-- To start in docker, run `docker-compose up` in the project directory. -->

## Documentation

TODO

## Authors

- **Fedor Kuyanov**([@kuyanov](https://github.com/kuyanov))
- **Andrei Odintsov** ([@Forestryks](https://github.com/Forestryks))

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



FROM ubuntu:19.10

RUN apt-get update && \
    apt-get -y install git build-essential cmake bsdmainutils python3 && \
    rm -rf /var/lib/apt/lists/*

COPY . /tools
WORKDIR /tools/libsbox/daemon

RUN mkdir -p build && cd build && rm -rf * && \
    cmake .. && \
    make && yes | make install

ENTRYPOINT [ "libsboxd" ]

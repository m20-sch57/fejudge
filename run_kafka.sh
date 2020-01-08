#!/bin/bash

echo -e "Stopping servers..."
$1/bin/kafka-server-stop.sh
$1/bin/zookeeper-server-stop.sh
echo -e "Completed.\n"

echo -e "Deleting /tmp/kafka-logs..."
rm -rf /tmp/kafka-logs
echo -e "Completed.\n"

echo -e "Starting zookeeper..."
$1/bin/zookeeper-server-start.sh -daemon $1/config/zookeeper.properties
echo -e "Completed.\n"

echo "Starting kafka server..."
while ! nc -z localhost 2181; do echo "Connecting to localhost:2181..." && sleep 5; done && \
$1/bin/kafka-server-start.sh -daemon $1/config/server.properties
echo -e "Completed.\n"

echo -e "Creating topic judge (optional)..."
$1/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic judge
echo -e "Completed.\n"

exit 0

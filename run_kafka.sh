#!/bin/bash

echo -e "Stopping servers..."
$1/bin/kafka-server-stop.sh
$1/bin/zookeeper-server-stop.sh
sleep 2
echo -e "Completed.\n"

echo -e "Deleting /tmp/kafka-logs..."
rm -rf /tmp/kafka-logs
echo -e "Completed.\n"

echo -e "Starting zookeeper..."
$1/bin/zookeeper-server-start.sh -daemon $1/config/zookeeper.properties
sleep 10
echo -e "Completed.\n"

echo "Starting kafka server..."
$1/bin/kafka-server-start.sh -daemon $1/config/server.properties
sleep 2
echo -e "Completed.\n"

echo -e "Creating topic judge (optional)..."
$1/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic judge
echo -e "Completed.\n"

exit 0

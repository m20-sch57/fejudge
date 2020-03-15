import sys
import json

from kafka import KafkaConsumer

sys.path.append('..')
from libsbox import Libsbox
from config import Config


libsbox = Libsbox()
consumer = KafkaConsumer(
    'packages',
    bootstrap_servers=[Config.KAFKA_SERVER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    auto_commit_interval_ms=2000,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(0, 10)
)

for message in consumer:
    print(message.value['source'], flush=True)

import os


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'

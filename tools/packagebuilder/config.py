import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    PROBLEMS_UPLOAD_PATH = os.path.join(DATA_DIR, 'upload', 'problems')

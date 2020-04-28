import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    PROBLEMS_UPLOAD_PATH = os.path.join(DATA_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')

    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 10000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144

    GENERATOR_EXECUTION_TIME_LIMIT_MS = os.environ.get('GENERATOR_EXECUTION_TIME_LIMIT_MS') or 5000
    GENERATOR_EXECUTION_MEMORY_LIMIT_KB = os.environ.get('GENERATOR_EXECUTION_MEMORY_LIMIT_KB') or 524288

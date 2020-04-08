import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_DIR, 'database.db')

    SUBMISSIONS_LOG_PATH = os.path.join(DATA_DIR, 'logs', 'submissions')

    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 10000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144
    CHECKER_TIME_LIMIT_MS = os.environ.get('CHECKER_TIME_LIMIT_MS') or 1000
    CHECKER_MEMORY_LIMIT_KB = os.environ.get('CHECKER_MEMORY_LIMIT_KB') or 262144

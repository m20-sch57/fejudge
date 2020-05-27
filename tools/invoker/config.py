import os


class Config(object):
    NATS_SERVER = os.environ.get('NATS_SERVER') or 'nats://localhost:4222'
    DATA_DIR = os.environ.get('DATA_DIR')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'database.db')

    SUBMISSIONS_LOG_PATH = os.path.join(DATA_DIR, 'logs', 'submissions')

    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 10000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144

    CHECKER_EXECUTION_TIME_LIMIT_MS = os.environ.get('CHECKER_EXECUTION_TIME_LIMIT_MS') or 2000
    CHECKER_EXECUTION_MEMORY_LIMIT_KB = os.environ.get('CHECKER_EXECUTION_MEMORY_LIMIT_KB') or 524288

import os


basedir = os.path.dirname(__file__)


class Config(object):
    # Identity
    INVOKER_NAME = os.environ.get('INVOKER_NAME') or 'invoker'

    # NATS server
    NATS_SERVER = os.environ.get('NATS_SERVER') or 'nats://localhost:4222'

    # Libsbox
    LIBSBOX_SOCKET = os.environ.get('LIBSBOX_SOCKET') or '/etc/libsboxd/socket'
    LIBSBOX_DIR = os.path.join(basedir, 'sandbox', INVOKER_NAME)

    # Data
    DATA_DIR = os.environ.get('DATA_DIR')
    PROBLEMS_UPLOAD_PATH = os.path.join(DATA_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'database.db')

    # Default compilation and execution limits
    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 30000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144
    CHECKER_EXECUTION_TIME_LIMIT_MS = os.environ.get('CHECKER_EXECUTION_TIME_LIMIT_MS') or 5000
    CHECKER_EXECUTION_MEMORY_LIMIT_KB = os.environ.get('CHECKER_EXECUTION_MEMORY_LIMIT_KB') or 524288
    GENERATOR_EXECUTION_TIME_LIMIT_MS = os.environ.get('GENERATOR_EXECUTION_TIME_LIMIT_MS') or 5000
    GENERATOR_EXECUTION_MEMORY_LIMIT_KB = os.environ.get('GENERATOR_EXECUTION_MEMORY_LIMIT_KB') or 524288

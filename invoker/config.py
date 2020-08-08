import os


basedir = os.path.dirname(__file__)


class Config(object):
    # Identity
    INVOKER_NAME = os.environ.get('INVOKER_NAME') or 'invoker'

    # Socketio server
    SOCKETIO_URL = os.environ.get('SOCKETIO_URL') or 'http://localhost:3113'

    # NATS server
    NATS_URL = os.environ.get('NATS_URL') or 'nats://localhost:4222'

    # Libsbox
    LIBSBOX_SOCKET = os.environ.get('LIBSBOX_SOCKET') or '/etc/libsboxd/socket'
    LIBSBOX_DIR = os.path.join(basedir, 'sandbox', INVOKER_NAME)

    # Storage
    STORAGE_DIR = os.environ.get('STORAGE_DIR') or ''
    PROBLEMS_UPLOAD_PATH = os.path.join(STORAGE_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(STORAGE_DIR, 'problems')

    # SQLAlchemy database
    POSTGRES_URL = os.environ.get('POSTGRES_URL') or 'localhost:5432'
    POSTGRES_USER = os.environ.get('POSTGRES_USER') or 'postgres'
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD') or 'postgres'
    POSTGRES_DB = os.environ.get('POSTGRES_DB') or 'database.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{url}/{db}'.format(
        user=POSTGRES_USER, password=POSTGRES_PASSWORD, url=POSTGRES_URL, db=POSTGRES_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default compilation and execution limits
    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 30000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144
    CHECKER_EXECUTION_TIME_LIMIT_MS = os.environ.get('CHECKER_EXECUTION_TIME_LIMIT_MS') or 5000
    CHECKER_EXECUTION_MEMORY_LIMIT_KB = os.environ.get('CHECKER_EXECUTION_MEMORY_LIMIT_KB') or 524288
    GENERATOR_EXECUTION_TIME_LIMIT_MS = os.environ.get('GENERATOR_EXECUTION_TIME_LIMIT_MS') or 5000
    GENERATOR_EXECUTION_MEMORY_LIMIT_KB = os.environ.get('GENERATOR_EXECUTION_MEMORY_LIMIT_KB') or 524288

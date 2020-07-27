import os


basedir = os.path.dirname(__file__)


class Config(object):
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'surprise!'
    MAX_CONTENT_LENGTH = 1024 * 65536

    # Logging
    LOG_FILE = 'logs/app.log'

    # Max submission size
    MAX_SUBMISSION_SIZE = 1024 * 1024

    # Mail server
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''

    # NATS server
    NATS_SERVER = os.environ.get('NATS_SERVER') or 'nats://localhost:4222'

    # Data
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    AVATARS_SAVE_PATH = os.path.join(DATA_DIR, 'avatars')
    SUBMISSIONS_DOWNLOAD_PATH = os.path.join(DATA_DIR, 'download', 'submissions')
    PROBLEMS_UPLOAD_PATH = os.path.join(DATA_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')

    # SQLAlchemy database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NAMING_CONVENTION = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

import os


basedir = os.path.dirname(__file__)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'h438d95hakfjd90b'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'fejudge.system@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    NATS_SERVER = os.environ.get('NATS_SERVER') or 'nats://localhost:4222'

    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AVATARS_SAVE_PATH = os.path.join(DATA_DIR, 'avatars')
    SUBMISSIONS_LOG_PATH = os.path.join(DATA_DIR, 'logs', 'submissions')
    SUBMISSIONS_DOWNLOAD_PATH = os.path.join(DATA_DIR, 'download', 'submissions')
    PROBLEMS_UPLOAD_PATH = os.path.join(DATA_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')

    MAX_CONTENT_LENGTH = 1024 * 65536

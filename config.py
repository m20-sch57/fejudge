import os


basedir = os.path.dirname(__file__)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'h438d95hakfjd90b'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'fejudge.system@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AVATARS_SAVE_PATH = os.environ.get('AVATARS_SAVE_PATH') or \
        os.path.join(basedir, 'avatars')
    SUBMISSIONS_LOG_PATH = os.environ.get('SUBMISSIONS_LOG_PATH') or \
        os.path.join(basedir, 'logs', 'submissions')
    SUBMISSIONS_DOWNLOAD_PATH = os.environ.get('SUBMISSIONS_DOWNLOAD_PATH') or \
        os.path.join(basedir, 'download', 'submissions')
    PROBLEMS_PATH = os.environ.get('PROBLEMS_PATH') or \
        os.path.join(basedir, 'problems')
    MAX_CONTENT_LENGTH = os.environ.get('MAX_CONTENT_LENGTH') or 1024 * 256

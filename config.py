import os


basedir = os.path.dirname(__file__)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'h438d95hakfjd90b'
    SYSTEM_EMAIL = os.environ.get('SYSTEM_EMAIL') or 'fejudge.system@gmail.com'
    SYSTEM_EMAIL_PASSWORD = os.environ.get('SYSTEM_EMAIL_PASSWORD') or 'Fedroadmin'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AVATARS_SAVE_PATH = os.environ.get('AVATARS_SAVE_PATH') or \
        os.path.join(basedir, 'avatars')
    SUBMISSIONS_EXEC_PATH = os.environ.get('SUBMISSIONS_EXEC_PATH') or \
        os.path.join(basedir, 'submissions')
    SUBMISSIONS_LOG_PATH = os.environ.get('SUBMISSIONS_LOG_PATH') or \
        os.path.join(basedir, 'logs', 'submissions')
    SUBMISSIONS_DOWNLOAD_PATH = os.environ.get('SUBMISSIONS_DOWNLOAD_PATH') or \
        os.path.join(basedir, 'download', 'submissions')
    PROBLEMS_PATH = os.environ.get('PROBLEMS_PATH') or \
        os.path.join(basedir, 'problems')
    MAX_CONTENT_LENGTH = os.environ.get('MAX_CONTENT_LENGTH') or 1024 * 256

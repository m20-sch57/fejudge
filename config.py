import os


basedir = os.path.dirname(__file__)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'h438d95hakfjd90b'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AVATARS_SAVE_PATH = os.environ.get('AVATARS_SAVE_PATH') or os.path.join(basedir, 'avatars')
    MAX_CONTENT_LENGTH = os.environ.get('MAX_CONTENT_LENGTH') or 1024 * 256

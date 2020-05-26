import os


class Config(object):
    DATA_DIR = os.environ.get('DATA_DIR')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')

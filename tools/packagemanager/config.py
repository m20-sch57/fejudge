import os
import sys


basedir = os.path.dirname(sys.modules['__main__'].__file__)


class Config(object):
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')

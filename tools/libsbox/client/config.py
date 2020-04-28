import os
import sys


basedir = os.path.dirname(sys.modules['__main__'].__file__)


class Config(object):
    SOCKET_FILE = os.environ.get('SOCKET_FILE') or '/etc/libsboxd/socket'
    LIBSBOX_DIR = os.environ.get('LIBSBOX_DIR') or \
        os.path.abspath(os.path.join(basedir, 'container', str(os.getpid())))

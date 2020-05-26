import os


class Config(object):
    SOCKET_FILE = os.environ.get('SOCKET_FILE') or '/etc/libsboxd/socket'
    SANDBOX_DIR = os.environ.get('SANDBOX_DIR')
    LIBSBOX_DIR = os.path.abspath(os.path.join(SANDBOX_DIR, str(os.getpid())))

import os


class Config(object):
    SOCKET_FILE = os.environ.get('SOCKET_FILE') or '/etc/libsboxd/socket'

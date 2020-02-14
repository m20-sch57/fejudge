import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    SOCKET_FILE = os.environ.get('SOCKET_FILE') or '/etc/libsboxd/socket'
    SUBMISSION_DIR = os.environ.get('SUBMISSION_DIR') or \
        os.path.join(basedir, 'submission')
    SUBMISSION_INPUT = os.environ.get('SUBMISSION_INPUT') or \
        os.path.join(SUBMISSION_DIR, 'input.txt')
    SUBMISSION_OUTPUT = os.environ.get('SUBMISSION_OUTPUT') or \
        os.path.join(SUBMISSION_DIR, 'output.txt')
    SUBMISSION_ANSWER = os.environ.get('SUBMISSION_ANSWER') or \
        os.path.join(SUBMISSION_DIR, 'answer.txt')
    SUBMISSION_RESULT = os.environ.get('SUBMISSION_RESULT') or \
        os.path.join(SUBMISSION_DIR, 'result.txt')
    SUBMISSION_ERROR = os.environ.get('SUBMISSION_ERROR') or \
        os.path.join(SUBMISSION_DIR, 'error.txt')
    SUBMISSION_CHECKER = os.environ.get('SUBMISSION_CHECKER') or \
        os.path.join(SUBMISSION_DIR, 'checker.out')

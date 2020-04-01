import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    PROBLEMS_UPLOAD_PATH = os.path.join(DATA_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')
    PROBLEM_DIR = os.path.join(basedir, 'problem')

    CHECKER_SOURCE_RELPATH = 'checker'
    CHECKER_SOURCE_PATH = os.path.join(PROBLEM_DIR, CHECKER_SOURCE_RELPATH)
    CHECKER_BINARY_RELPATH = 'checker.out'
    CHECKER_BINARY_PATH = os.path.join(PROBLEM_DIR, CHECKER_BINARY_RELPATH)
    TESTLIB_RELPATH = 'testlib.h'
    TESTLIB_PATH = os.path.join(PROBLEM_DIR, TESTLIB_RELPATH)
    ERROR_RELPATH = 'error.txt'
    ERROR_PATH = os.path.join(PROBLEM_DIR, ERROR_RELPATH)

    CHECKER_COMPILATION_TIME_LIMIT_MS = os.environ.get('CHECKER_COMPILATION_TIME_LIMIT_MS') or 10000
    CHECKER_COMPILATION_MEMORY_LIMIT_KB = os.environ.get('CHECKER_COMPILATION_MEMORY_LIMIT_KB') or 262144

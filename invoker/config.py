import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    JUDGE_SERVER = os.environ.get('JUDGE_SERVER') or 'localhost:3113'
    SOCKET_FILE = os.environ.get('SOCKET_FILE') or '/etc/libsboxd/socket'

    SUBMISSION_INPUT_NAME = os.environ.get('SUBMISSION_INPUT_NAME') or 'input.txt'
    SUBMISSION_OUTPUT_NAME = os.environ.get('SUBMISSION_OUTPUT_NAME') or 'output.txt'
    SUBMISSION_ANSWER_NAME = os.environ.get('SUBMISSION_ANSWER_NAME') or 'answer.txt'
    SUBMISSION_RESULT_NAME = os.environ.get('SUBMISSION_RESULT_NAME') or 'result.txt'
    SUBMISSION_ERROR_NAME = os.environ.get('SUBMISSION_ERROR_NAME') or 'error.txt'
    SUBMISSION_CHECKER_NAME = os.environ.get('SUBMISSION_CHECKER_NAME') or 'checker.out'

    SUBMISSION_DIR = os.environ.get('SUBMISSION_DIR') or \
        os.path.join(basedir, 'submission')
    SUBMISSION_INPUT = os.path.join(SUBMISSION_DIR, SUBMISSION_INPUT_NAME)
    SUBMISSION_OUTPUT = os.path.join(SUBMISSION_DIR, SUBMISSION_OUTPUT_NAME)
    SUBMISSION_ANSWER = os.path.join(SUBMISSION_DIR, SUBMISSION_ANSWER_NAME)
    SUBMISSION_RESULT = os.path.join(SUBMISSION_DIR, SUBMISSION_RESULT_NAME)
    SUBMISSION_ERROR = os.path.join(SUBMISSION_DIR, SUBMISSION_ERROR_NAME)
    SUBMISSION_CHECKER = os.path.join(SUBMISSION_DIR, SUBMISSION_CHECKER_NAME)

    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 10000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144
    CHECKER_TIME_LIMIT_MS = os.environ.get('CHECKER_TIME_LIMIT_MS') or 1000
    CHECKER_MEMORY_LIMIT_KB = os.environ.get('CHECKER_MEMORY_LIMIT_KB') or 262144

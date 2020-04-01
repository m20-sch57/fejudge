import os


basedir = os.path.dirname(__file__)


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_DIR, 'database.db')

    SUBMISSIONS_LOG_PATH = os.path.join(DATA_DIR, 'logs', 'submissions')
    SUBMISSION_DIR = os.path.join(basedir, 'submission')

    PARTICIPANT_SOURCE_RELPATH = 'participant'
    PARTICIPANT_SOURCE_PATH = os.path.join(SUBMISSION_DIR, PARTICIPANT_SOURCE_RELPATH)
    PARTICIPANT_BINARY_RELPATH = 'participant.out'
    PARTICIPANT_BINARY_PATH = os.path.join(SUBMISSION_DIR, PARTICIPANT_BINARY_RELPATH)
    CHECKER_BINARY_RELPATH = 'checker.out'
    CHECKER_BINARY_PATH = os.path.join(SUBMISSION_DIR, CHECKER_BINARY_RELPATH)
    INPUT_RELPATH = 'input.txt'
    INPUT_PATH = os.path.join(SUBMISSION_DIR, INPUT_RELPATH)
    OUTPUT_RELPATH = 'output.txt'
    OUTPUT_PATH = os.path.join(SUBMISSION_DIR, OUTPUT_RELPATH)
    ERROR_RELPATH = 'error.txt'
    ERROR_PATH = os.path.join(SUBMISSION_DIR, ERROR_RELPATH)
    ANSWER_RELPATH = 'answer.txt'
    ANSWER_PATH = os.path.join(SUBMISSION_DIR, ANSWER_RELPATH)
    RESULT_RELPATH = 'result.txt'
    RESULT_PATH = os.path.join(SUBMISSION_DIR, RESULT_RELPATH)

    COMPILATION_TIME_LIMIT_MS = os.environ.get('COMPILATION_TIME_LIMIT_MS') or 10000
    COMPILATION_MEMORY_LIMIT_KB = os.environ.get('COMPILATION_MEMORY_LIMIT_KB') or 262144
    CHECKER_TIME_LIMIT_MS = os.environ.get('CHECKER_TIME_LIMIT_MS') or 1000
    CHECKER_MEMORY_LIMIT_KB = os.environ.get('CHECKER_MEMORY_LIMIT_KB') or 262144

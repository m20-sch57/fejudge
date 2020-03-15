import os


class Config(object):
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER') or 'localhost:9092'
    LOCAL_DIR = os.environ.get('LOCAL_DIR') or os.path.dirname(__file__)
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(os.getcwd(), 'data')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_DIR, 'database.db')

    PROBLEMS_PATH = os.path.join(DATA_DIR, 'problems')
    SUBMISSIONS_LOG_PATH = os.path.join(DATA_DIR, 'logs', 'submissions')
    SUBMISSION_DIR = os.path.join(LOCAL_DIR, 'submission')

    SUBMISSION_INPUT_NAME = 'input.txt'
    SUBMISSION_OUTPUT_NAME = 'output.txt'
    SUBMISSION_ANSWER_NAME = 'answer.txt'
    SUBMISSION_RESULT_NAME = 'result.txt'
    SUBMISSION_ERROR_NAME = 'error.txt'
    SUBMISSION_CHECKER_NAME = 'checker.out'
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

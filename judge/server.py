import os

from xmlrpc.server import SimpleXMLRPCServer

from app import app, db
from app.models import Submission


def tests_cnt(problem_id):
    path = os.path.join(
        app.config['PROBLEMS_PATH'],
        str(problem_id).zfill(6),
        'input'
    )
    return len(os.listdir(path))

def get_test_data(problem_id, test_number):
    test_input_file = os.path.join(
        app.config['PROBLEMS_PATH'],
        str(problem_id).zfill(6), 
        'input',
        str(test_number).zfill(3)
    )
    test_output_file = os.path.join(
        app.config['PROBLEMS_PATH'],
        str(problem_id).zfill(6),
        'output',
        str(test_number).zfill(3) + '.a'
    )
    return {
        'input': open(test_input_file).read(),
        'output': open(test_output_file).read()
    }

def get_checker_binary(problem_id):
    path = os.path.join(
        app.config['PROBLEMS_PATH'],
        str(problem_id).zfill(6),
        'checker.out'
    )
    return open(path, 'rb').read()

def set_submission_result(submission_id, status, score):
    submission = Submission.query.filter_by(id=submission_id).first()
    if submission is None:
        return False
    submission.status = status
    submission.score = score
    db.session.commit()
    return True

def set_submission_details(submission_id, details):
    submission = Submission.query.filter_by(id=submission_id).first()
    if submission is None:
        return False
    submission.set_details(details)
    db.session.commit()
    return True

def write_logs(submission_id, data):
    path = os.path.join(
        app.config['SUBMISSIONS_LOG_PATH'],
        str(submission_id).zfill(6) + '.txt'
    )
    open(path, 'a').write(data)
    return True


class JudgeServer:
    def __init__(self):
        self.server = None

    def run(self, host, port):
        self.server = SimpleXMLRPCServer((host, port))
        self.server.register_function(tests_cnt)
        self.server.register_function(get_test_data)
        self.server.register_function(get_checker_binary)
        self.server.register_function(set_submission_result)
        self.server.register_function(set_submission_details)
        self.server.register_function(write_logs)
        self.server.serve_forever()

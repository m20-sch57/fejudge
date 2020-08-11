from invoker import session, sio
from models import Submission, Problem


def commit_session():
    session.commit()


def get_submission_by_id(submission_id):
    return session.query(Submission).filter_by(id=submission_id).first()


def get_problem_by_id(problem_id):
    return session.query(Problem).filter_by(id=problem_id).first()


def send_compiling_event(submission_id):
    sio.emit('compiling', submission_id)


def send_evaluating_event(submission_id):
    sio.emit('evaluating', submission_id)


def send_completed_event(submission_id):
    sio.emit('completed', submission_id)

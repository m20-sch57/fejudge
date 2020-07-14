from flask_login import current_user
from flask_socketio import emit, join_room

from app import socketio
from app.models import Submission


def get_user_by_submission_id(submission_id):
    return Submission.query.filter_by(id=submission_id).first().user.id


def get_problem_by_submission_id(submission_id):
    return Submission.query.filter_by(id=submission_id).first().problem.id


def build_room(user_id, problem_id):
    return '{}:{}'.format(user_id, problem_id)


@socketio.on('join')
def join(problem_id):
    room = build_room(current_user.id, problem_id)
    join_room(room)


@socketio.on('compiling')
def compiling(submission_id):
    user_id = get_user_by_submission_id(submission_id)
    problem_id = get_problem_by_submission_id(submission_id)
    room = build_room(user_id, problem_id)
    emit('compiling', {
        'submission_id': submission_id
    }, room=room)


@socketio.on('evaluating')
def evaluating(submission_id):
    user_id = get_user_by_submission_id(submission_id)
    problem_id = get_problem_by_submission_id(submission_id)
    room = build_room(user_id, problem_id)
    emit('evaluating', {
        'submission_id': submission_id
    }, room=room)


@socketio.on('completed')
def completed(submission_id, submission_status, submission_score):
    user_id = get_user_by_submission_id(submission_id)
    problem_id = get_problem_by_submission_id(submission_id)
    room = build_room(user_id, problem_id)
    emit('completed', {
        'submission_id': submission_id,
        'submission_status': submission_status,
        'submission_score': submission_score
    }, room=room)

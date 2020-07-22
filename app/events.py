from flask_login import current_user
from flask_socketio import emit, join_room

from app import socketio
from app.queries import get_submission_by_id


def build_room(user_id, problem_id):
    return '{}:{}'.format(user_id, problem_id)


@socketio.on('join')
def join(problem_id):
    room = build_room(current_user.id, problem_id)
    join_room(room)


def new_submission(submission_id):
    submission = get_submission_by_id(submission_id)
    if not submission:
        return
    room = build_room(submission.user.id, submission.problem.id)
    socketio.emit('new_submission', {
        'submission_id': submission.id,
        'submission_language': submission.language
    }, room=room)


@socketio.on('compiling')
def compiling(submission_id):
    submission = get_submission_by_id(submission_id)
    if not submission:
        return
    room = build_room(submission.user.id, submission.problem.id)
    emit('compiling', {
        'submission_id': submission_id
    }, room=room)


@socketio.on('evaluating')
def evaluating(submission_id):
    submission = get_submission_by_id(submission_id)
    if not submission:
        return
    room = build_room(submission.user.id, submission.problem.id)
    emit('evaluating', {
        'submission_id': submission_id
    }, room=room)


@socketio.on('completed')
def completed(submission_id):
    submission = get_submission_by_id(submission_id)
    if not submission:
        return
    room = build_room(submission.user.id, submission.problem.id)
    emit('completed', {
        'submission_id': submission_id,
        'submission_status': submission.status,
        'submission_score': submission.score
    }, room=room)

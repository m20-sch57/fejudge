import json

from flask_login import current_user
from flask_socketio import emit, join_room

from app import socketio
from app.models import Submission


def get_user_by_submission_id(submission_id):
    return Submission.query.filter_by(id=submission_id).first().user


@socketio.on('join')
def join():
    join_room(current_user.id)

@socketio.on('compiling')
def compiling(submission_id):
    user_id = get_user_by_submission_id(submission_id).id
    emit('compiling', submission_id, room=user_id)

@socketio.on('evaluating')
def evaluating(submission_id):
    user_id = get_user_by_submission_id(submission_id).id
    emit('evaluating', submission_id, room=user_id)

@socketio.on('completed')
def completed(submission_id):
    user_id = get_user_by_submission_id(submission_id).id
    emit('completed', submission_id, room=user_id)

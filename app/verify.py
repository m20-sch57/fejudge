from flask import flash, abort

from app import app
from app.queries import get_user_by_username, get_user_by_email


def verify_login(username, password):
    user = get_user_by_username(username)
    if user is None or not user.check_password(password):
        flash('Incorrect username or password', category='failure auto-dismiss')
        return False
    return True


def verify_register(username, email, password):
    if not username:
        flash('Username should not be empty', category='failure')
        return False
    if get_user_by_username(username) is not None:
        flash('Your username is already occupied', category='failure')
        return False
    if email.find('@') == -1:
        flash('Please type in valid email address', category='failure')
        return False
    if get_user_by_email(email) is not None:
        flash('Your email is already occupied', category='failure')
        return False
    if len(password) < 8:
        flash('Your password is too short, consider changing it later', category='warning')
    return True


def verify_submit(source_blob, language):
    if len(source_blob) > app.config['MAX_SUBMISSION_SIZE']:
        abort(413)
    try:
        source_blob.decode('utf-8')
    except UnicodeDecodeError:
        abort(400)
    if language not in ['cpp', 'py']: # TODO: adjust for problem
        abort(400)

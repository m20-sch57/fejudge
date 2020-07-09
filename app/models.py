import json

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import date, datetime, timedelta

import constants
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    first_name = db.Column(db.String(128), default='')
    last_name = db.Column(db.String(128), default='')
    password_hash = db.Column(db.String(128))

    avatar = db.Column(db.String(64), default='user.png')
    email = db.Column(db.String(128), unique=True)
    active_language = db.Column(db.String(16), default='cpp')

    restore_tokens = db.relationship('RestoreToken', backref='user', lazy='dynamic')
    contest_requests = db.relationship('ContestRequest', backref='user', lazy='dynamic')
    owned_contests = db.relationship('Contest', backref='owner', lazy='dynamic')
    submissions = db.relationship('Submission', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<USER {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class RestoreToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(10))
    time = db.Column(db.DateTime)

    def __repr__(self):
        return '<RESTORE_TOKEN USER={} CODE={}>'.format(self.user_id, self.code)

    @staticmethod
    def get_token(user):
        return RestoreToken.query.filter_by(user=user).order_by(desc(RestoreToken.time)).first()


class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String(64), unique=True)
    contest_type = db.Column(db.String(16))
    start_time = db.Column(db.DateTime)
    duration = db.Column(db.Interval)

    contest_requests = db.relationship('ContestRequest', backref='contest', lazy='dynamic')
    problems = db.relationship('Problem', backref='contest', lazy='dynamic')
    submissions = db.relationship('Submission', backref='contest', lazy='dynamic')

    def __repr__(self):
        return '<CONTEST {}>'.format(self.name)

    def duration_in_minutes(self):
        return int(self.duration.total_seconds() / 60)

    def total_score(self, user):
        score = 0
        for problem in self.problems:
            score += problem.score(user)
        return score

    def total_maxscore(self):
        max_score = 0
        for problem in self.problems:
            max_score += problem.max_score
        return max_score


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))

    problem_type = db.Column(db.String(16))
    status = db.Column(db.String(16), default='')
    number = db.Column(db.Integer)
    names = db.Column(db.Text, default='{}')
    max_score = db.Column(db.Integer, default=100)
    max_submissions = db.Column(db.Integer, default=50)

    submissions = db.relationship('Submission', backref='problem', lazy='dynamic')

    def __repr__(self):
        return '<PROBLEM {}>'.format(self.id)

    def get_name(self, language='english'):
        names_dict = json.loads(self.names)
        if language in names_dict.keys():
            return names_dict[language]
        return next(iter(names_dict.values()))

    def last_submission(self, user):
        return self.submissions.filter_by(user=user).order_by(desc(Submission.time)).first()

    def max_submission(self, user):
        return self.submissions.filter_by(user=user).order_by(desc(Submission.score)).first()

    def submitted(self, user):
        return bool(self.last_submission(user))

    def score(self, user):
        submission = self.last_submission(user)
        return submission.score if submission else 0


class ContestRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<CONTEST_REQUEST CONTEST={} USER={} TIME={}>'.format(self.contest_id, self.user_id, self.start_time)

    def get_finish_time(self):
        return self.finish_time or self.start_time + self.contest.duration

    def state(self):
        current_time = datetime.utcnow().replace(microsecond=0)
        if current_time < self.start_time:
            return 'Not started'
        if current_time >= self.get_finish_time():
            return 'Finished'
        return 'In progress'

    def time_remaining(self):
        if self.state() != 'In progress':
            return timedelta()
        current_time = datetime.utcnow().replace(microsecond=0)
        return self.get_finish_time() - current_time

    def time_passed(self):
        if self.state() != 'In progress':
            return timedelta()
        current_time = datetime.utcnow().replace(microsecond=0)
        return current_time - self.start_time


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime)
    language = db.Column(db.String(16))
    source = db.Column(db.Text)
    status = db.Column(db.String(16))
    score = db.Column(db.Integer)
    details = db.Column(db.Text, default='{}')

    def __repr__(self):
        return '<SUBMISSION PROBLEM={} USER={} SCORE={}>'.format(self.problem_id, self.user_id, self.score)

    def time_from_start(self):
        contest_request = ContestRequest.query.filter_by(contest=self.contest, user=self.user).first_or_404()
        return self.time - contest_request.start_time

    def formatted_language(self):
        return constants.LANGUAGE_MATCHING[self.language]

    def formatted_status(self):
        return constants.STATUS_MATCHING[self.status]

    @staticmethod
    def formatted_test_status(test_status):
        return constants.STATUS_MATCHING[test_status]

    def show_score(self):
        return self.status not in ['In queue', 'Compiling']

    def is_judged(self):
        return self.status not in ['In queue', 'Compiling', 'Running']

    def get_details(self):
        return json.loads(self.details)

    # def set_details(self, details):
    #     self.details = json.dumps(details)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

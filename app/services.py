import json

from typing import Optional
from datetime import datetime, timedelta

from app import db, nats
from app.models import User, Contest, ContestRequest, Problem, Submission


def get_user_by_username(username: str) -> Optional[User]:
    return User.query.filter_by(username=username).first()


def get_user_by_email(email: str) -> Optional[User]:
    return User.query.filter_by(email=email).first()


def get_contest_by_id_or_404(contest_id: int) -> Optional[Contest]:
    return Contest.query.filter_by(id=contest_id).first_or_404()


def get_contest_request(contest: Contest, user: User) -> Optional[ContestRequest]:
    return ContestRequest.query.filter_by(contest_id=contest.id, user_id=user.id).first()


def get_contests_for_user(user: User) -> list:
    return [(contest, get_contest_request(contest, user)) for contest in Contest.query.all()]


def get_problem_by_number_or_404(contest: Contest, number: int) -> Optional[Problem]:
    return Problem.query.filter_by(contest=contest, number=number).first_or_404()


def get_submission_by_id(submission_id: int) -> Optional[Submission]:
    return Submission.query.filter_by(id=submission_id).first()


def get_submissions_by_problem_user(problem: Problem, user: User) -> list:
    return Submission.query.filter_by(problem=problem, user=user).order_by(Submission.time.desc())


def register_user(username: str, email: str, password: str) -> User:
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def create_contest_request(contest: Contest, user: User) -> ContestRequest:
    contest_request = ContestRequest(
        contest=contest,
        user=user,
        start_time=datetime.utcnow()
    )
    db.session.commit()
    return contest_request


def create_submission(contest: Contest, problem: Problem, user: User, language: str, source: str) -> Submission:
    submission = Submission(
        contest=contest,
        problem=problem,
        user=user,
        language=language,
        source=source,
        time=datetime.utcnow(),
        status='in_queue',
        score=0
    )
    db.session.add(submission)
    db.session.commit()
    return submission


def create_problem(contest: Contest, problem_type: str) -> Problem:
    problem = Problem(
        contest=contest,
        problem_type=problem_type,
        number=contest.problems.count() + 1,
        status='pending'
    )
    db.session.add(problem)
    db.session.commit()
    return problem


def create_contest(name: str, contest_type: str, duration: timedelta, owner: User) -> Contest:
    contest = Contest(
        name=name,
        contest_type=contest_type,
        duration=duration,
        owner=owner
    )
    db.session.add(contest)
    db.session.commit()
    return contest


def submit_to_queue(group, obj):
    nats.connect()
    nats.publish(group, payload=json.dumps(obj).encode('utf-8'))
    nats.close()


def evaluate_submission(submission):
    submit_to_queue(group='invokers', obj={
        'type': 'evaluate',
        'submission_id': submission.id
    })


def initialize_problem(problem):
    submit_to_queue(group='invokers', obj={
        'type': 'problem_init',
        'problem_id': problem.id
    })

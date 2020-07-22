from app.models import User, Contest, ContestRequest, Problem, Submission


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_contest_by_id_or_404(contest_id):
    return Contest.query.filter_by(id=contest_id).first_or_404()


def get_contest_request(contest, user):
    return ContestRequest.query.filter_by(contest_id=contest.id, user_id=user.id).first()


def get_contests_for_user(user):
    return [(contest, get_contest_request(contest, user)) for contest in Contest.query.all()]


def get_problem_by_number_or_404(contest, number):
    return Problem.query.filter_by(contest=contest, number=number).first_or_404()


def get_submission_by_id(submission_id):
    return Submission.query.filter_by(id=submission_id).first()


def get_submissions_by_problem_user(problem, user):
    return Submission.query.filter_by(
        problem=problem, user=user).order_by(Submission.time.desc())

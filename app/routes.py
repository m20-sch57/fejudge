import os
# import strgen

from functools import wraps
from flask import render_template, redirect, abort, url_for, request, flash, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta

from app import app, db, avatars
from app import submit_to_queue
# from app.forms import LoginForm, RegistrationForm, RestorePasswordForm, VerificationCodeForm
# from app.forms import EditAvatarForm, EditProfileForm, EditPasswordForm
# from app.forms import InputProblemForm, FileProblemForm
from app.forms import AdminInfoForm, UploadPackageForm
from app.models import User, RestoreToken, Contest, Problem, ContestRequest, Submission
from app.email import send_verification_code, send_new_password


@app.errorhandler(403)
def resource_forbidden(error):
    return render_template('error.html', page='error', message='Requested resource is forbidden.', code=403), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', page='error', message='Oops! Page not found.', code=404), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('error.html', page='error', message='Method not allowed.', code=405), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('error.html', page='error', message='File is too large.', code=413), 413


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', page='error', message='Oops! Internal server error.', code=500), 500


# @app.route('/')
# @app.route('/welcome')
# def welcome():
#     return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('contests_page'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Incorrect username or password', category='failure auto-dismiss')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('contests_page'))
    return render_template('login_new.html', page='login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('contests_page'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not username:
            flash('Username should not be empty', category='failure')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first() is not None:
            flash('Your username is already occupied', category='failure')
            return redirect(url_for('register'))
        if email.find('@') == -1:
            flash('Please type in valid email address', category='failure')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first() is not None:
            flash('Your email is already occupied', category='failure')
            return redirect(url_for('register'))
        if len(password) < 8:
            flash('Your password is too short, consider changing it later', category='warning')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered', category='success auto-dismiss')
        return redirect(url_for('login'))
    return render_template('register_new.html', page='register')


# @app.route('/restorePassword', methods=['GET', 'POST'])
# def restore_password_welcome():
#     form = RestorePasswordForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None:
#             flash('Incorrect username', category='alert-danger')
#             return redirect(url_for('restore_password_welcome'))
#         current_time = datetime.utcnow().replace(microsecond=0)
#         code = strgen.StringGenerator('[0-9]{10}').render()
#         restore_token = RestoreToken(user=user, code=code, time=current_time)
#         send_verification_code(user.email, user.first_name, code)
#         db.session.commit()
#         return redirect(url_for('restore_password_selected', username=user.username))
#     return render_template('restore_password.html', title='Restore password', form=form)


# @app.route('/restorePassword/<username>', methods=['GET', 'POST'])
# def restore_password_selected(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     form = VerificationCodeForm()
#     if form.validate_on_submit():
#         code = form.code.data
#         restore_token = RestoreToken.get_token(user)
#         if restore_token is None:
#             flash('Error while finding selected user', category='alert-danger')
#             return redirect(url_for('restore_password_welcome'))
#         if code != restore_token.code:
#             flash('Code is incorrect, try again', category='alert-danger')
#             return redirect(url_for('restore_password_selected', username=username))
#         new_password = strgen.StringGenerator('[\w\d]{16}').render()
#         user.set_password(new_password)
#         send_new_password(user.email, user.first_name, new_password)
#         db.session.commit()
#         flash('New password has been sent to you by email', category='alert-success')
#         return redirect(url_for('logout'))
#     return render_template('verify.html', title='Restore password', form=form, user=user)


# @app.route('/changePassword', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     form = EditPasswordForm()
#     if form.validate_on_submit():
#         if not current_user.check_password(form.old_password.data):
#             flash('Incorrect password', category='alert-danger')
#             return redirect(url_for('change_password'))
#         current_user.set_password(form.new_password.data)
#         db.session.commit()
#         flash('Password has been successfully changed', category='alert-success')
#         return redirect(url_for('logout'))
#     return render_template('change_password.html', title='Change password', form=form)


# @app.route('/user/<username>')
# def profile_page(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     avatar_form = EditAvatarForm()
#     profile_form = EditProfileForm(user.email)
#     return render_template('user.html', title='View profile', user=user, 
#         avatar_form=avatar_form, profile_form=profile_form)


# @app.route('/avatars/<filename>')
# def avatar(filename):
#     return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


# @app.route('/changeAvatar', methods=['POST'])
# @login_required
# def change_avatar():
#     form = EditAvatarForm()
#     if form.validate_on_submit():
#         filename = avatars.save_avatar(form.image.data)
#         current_user.avatar = filename
#         db.session.commit()
#         flash('Your avatar has been saved', category='alert-success')
#     else:
#         flash('Data is incorrect', category='alert-danger')
#     return redirect(url_for('profile_page', username=current_user.username))


# @app.route('/changeProfile', methods=['POST'])
# @login_required
# def change_profile():
#     form = EditProfileForm(current_user.email)
#     if form.validate_on_submit():
#         current_user.first_name = form.first_name.data
#         current_user.last_name = form.last_name.data
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('Your information has been saved', category='alert-success')
#     else:
#         flash('Data is incorrect', category='alert-danger')
#     return redirect(url_for('profile_page', username=current_user.username))


def get_contest_by_id(contest_id):
    return Contest.query.filter_by(id=contest_id).first_or_404()


def get_contest_request(contest):
    return ContestRequest.query.filter_by(contest_id=contest.id, user_id=current_user.id).first()


@app.route('/contests')
@login_required
def contests_page():
    contests = [(contest, get_contest_request(contest)) for contest in Contest.query.all()]
    return render_template('contests_new.html', page='contests', contests=contests)


@app.route('/contests/<contest_id>')
@login_required
def contest_page(contest_id):
    contest = get_contest_by_id(contest_id)
    contest_request = get_contest_request(contest)
    if contest_request is None:
        return render_template('contest_register.html', page='contest_register', contest=contest)
    if contest_request.state() == 'Not started':
        return render_template('contest_wait.html', page='contest_wait')
    return redirect(url_for('contest_problem', contest_id=contest_id, number=1))


@app.route('/contests/<contest_id>/participate')
@login_required
def participate(contest_id):
    contest = get_contest_by_id(contest_id)
    contest_request = get_contest_request(contest)
    if contest_request is not None:
        flash('You are already participating in the contest', category='failure')
        return redirect(url_for('contests_page'))
    contest_request = ContestRequest(contest=contest, user=current_user, 
        start_time=datetime.utcnow().replace(microsecond=0))
    db.session.commit()
    return redirect(url_for('contest_problem', contest_id=contest.id, number=1))


def participation_required(func):
    @wraps(func)
    def decorated_view(contest_id, *args, **kwargs):
        contest = get_contest_by_id(contest_id)
        contest_request = get_contest_request(contest)
        if contest_request is None or contest_request.state() == 'Not started':
            abort(403)
        return func(contest_id, *args, **kwargs)
    return decorated_view


@app.route('/contests/<contest_id>/<number>/problem')
@login_required
@participation_required
def contest_problem(contest_id, number):
    contest = get_contest_by_id(contest_id)
    contest_request = get_contest_request(contest)
    problem = Problem.query.filter_by(contest=contest, number=number).first_or_404()
    from invoker.problem_manage import ProblemManager
    problem_manager = ProblemManager(problem.id)
    if problem.problem_type == 'Programming':
        return render_template('problem.html', page='problem', contest=contest,
            contest_request=contest_request, problem=problem, problem_manager=problem_manager)
    else:
        pass


@app.route('/contests/<contest_id>/<number>/submit', methods=['POST'])
@login_required
@participation_required
def submit_problem(contest_id, number):
    source_blob = request.files['sourceFile'].read()
    if len(source_blob) > app.config['MAX_SUBMISSION_SIZE']:
        abort(413)
    return 'Something'


@app.route('/contests/<contest_id>/<number>/<resource>')
@login_required
@participation_required
def problem_resource(contest_id, number, resource):
    contest = get_contest_by_id(contest_id)
    problem = Problem.query.filter_by(contest=contest, number=number).first_or_404()
    from invoker.problem_manage import ProblemManager
    problem_manager = ProblemManager(problem.id)
    submissions = Submission.query.filter_by(problem=problem, user=current_user).order_by(Submission.time.desc())
    resource_dir = ''
    if resource.endswith('.css'):
        resource_dir = 'static/css'
    elif resource.endswith('.html'):
        resource_dir = problem_manager.html_dir()
    elif resource.endswith('.pdf'):
        resource_dir = problem_manager.pdf_dir()
    else:
        resource_dir = problem_manager.html_dir()
    return send_from_directory(resource_dir, resource)
    # if contest_request.state() == 'Finished':
    #     flash('Ваше участие в контесте завершено', category='alert-info')
    # if problem.problem_type == 'Programming':
    #     problem_form = FileProblemForm(language=current_user.active_language)
    #     return render_template('contest_problem_prog.html', title=contest.name, contest=contest,
    #         problem=problem, problem_manager=problem_manager, request=contest_request,
    #         submissions=submissions, form=problem_form)
    # elif problem.problem_type == 'Test':
    #     problem_form = InputProblemForm()
    #     return render_template('contest_problem_test.html', title=contest.name, contest=contest,
    #         problem=problem, request=contest_request, submissions=submissions, form=problem_form)


# @app.route('/download/submission/<submission_id>')
# @login_required
# def download_submission(submission_id):
#     submission = Submission.query.filter_by(id=submission_id).first_or_404()
#     if submission.user != current_user:
#         flash('Forbidden operation', category='alert-danger')
#         return redirect(url_for('contests_page'))
#     source = submission.source
#     download_folder = app.config['SUBMISSIONS_DOWNLOAD_PATH']
#     filename = str(submission_id).zfill(6) + '.' + submission.language
#     path = os.path.join(download_folder, filename)
#     open(path, 'w').write(source)
#     return send_from_directory(download_folder, filename, as_attachment=True)


# @app.route('/contests/<contest_id>/<number>/main/send', methods=['POST'])
# @login_required
# def send(contest_id, number):
#     contest = get_contest_by_id(contest_id)
#     contest_request = get_contest_request(contest)
#     problem = Problem.query.filter_by(contest=contest, number=number).first_or_404()
#     try:
#         if contest_request is None or contest_request.state() != 'In progress':
#             raise ValueError('You are not allowed to send submissions in this contest')
#         if problem.problem_type == 'Programming':
#             problem_form = FileProblemForm()
#             if not problem_form.validate_on_submit():
#                 raise ValueError('Form is not valid')
#             language = problem_form.language.data
#             source = problem_form.source.data.read().decode('utf-8')
#             current_time = datetime.utcnow().replace(microsecond=0)
#             submission = Submission(contest=contest, problem=problem, user=current_user, time=current_time, 
#                 language=language, status='In queue', score=0, source=source)
#             current_user.active_language = language
#             db.session.add(submission)
#             db.session.commit()
#             submit_to_queue(group='invokers', obj={
#                 'type': 'evaluate',
#                 'submission_id': submission.id
#             })
#             flash('Your solution has been sent', category='alert-success')
#     except ValueError as error:
#         flash('Submission error: ' + str(error), category='alert-danger')
#     return redirect(url_for('load_problem', contest_id=contest.id, number=number, attr='main'))


# @app.route('/contests/<contest_id>/finish')
# @login_required
# def finish_contest(contest_id):
#     contest = get_contest_by_id(contest_id)
#     contest_request = get_contest_request(contest)
#     if contest_request is None or contest_request.state() in ['Not started', 'Finished']:
#         flash('Forbidden operation', category='alert-danger')
#         return redirect(url_for('contests_page'))
#     current_time = datetime.utcnow().replace(microsecond=0)
#     contest_request.finish_time = current_time
#     db.session.commit()
#     return redirect(url_for('load_problem', contest_id=contest.id, number=1, attr='main'))


def contest_admin(func):
    @wraps(func)
    def decorated_view(contest_id, *args, **kwargs):
        contest = get_contest_by_id(contest_id)
        if contest.owner != current_user:
            flash('You do not have admin privileges', category='alert-danger')
            return redirect(url_for('contests_page'))
        return func(contest_id, *args, **kwargs)
    return decorated_view


@app.route('/contests/<contest_id>/admin', methods=['GET', 'POST'])
@app.route('/contests/<contest_id>/admin/info', methods=['GET', 'POST'])
@login_required
@contest_admin
def contest_admin_info(contest_id):
    contest = get_contest_by_id(contest_id)
    info_form = AdminInfoForm(contest.name, contest_type=contest.contest_type)
    if info_form.validate_on_submit():
        contest.name = info_form.name.data
        contest.contest_type = info_form.contest_type.data
        contest.duration = timedelta(minutes=info_form.duration.data)
        db.session.commit()
        flash('Contest info has been saved', category='alert-success')
    return render_template('contest_admin_info.html', title=contest.name, contest=contest, form=info_form)


@app.route('/contests/<contest_id>/admin/problems')
@login_required
@contest_admin
def contest_admin_problems(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_problems.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/participants')
@login_required
@contest_admin
def contest_admin_participants(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_participants.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/submissions')
@login_required
@contest_admin
def contest_admin_submissions(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_submissions.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/notifications')
@login_required
@contest_admin
def contest_admin_notifications(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_notifications.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/newproblem', methods=['GET', 'POST'])
@login_required
@contest_admin
def contest_admin_newproblem(contest_id):
    contest = get_contest_by_id(contest_id)
    upload_package_form = UploadPackageForm()
    if upload_package_form.validate_on_submit():
        new_problem = Problem(
            contest=contest, problem_type='Programming', number=contest.problems.count() + 1, status='Pending')
        db.session.add(new_problem)
        db.session.flush()
        upload_folder = app.config['PROBLEMS_UPLOAD_PATH']
        filename = str(new_problem.id) + '.zip'
        path = os.path.join(upload_folder, filename)
        upload_package_form.package.data.save(path)
        db.session.commit()
        submit_to_queue(group='invokers', obj={
            'type': 'problem_init',
            'problem_id': new_problem.id,
        })
        flash('Your package has been uploaded, check the status of the problem', category='alert-info')
        return redirect(url_for('contest_admin_problems', contest_id=contest_id))
    return render_template('contest_admin_newproblem.html',
        title='New problem', contest=contest, form=upload_package_form)

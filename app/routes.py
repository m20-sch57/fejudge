import os
from urllib.parse import unquote_plus
from flask import render_template, redirect, url_for, flash, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app import app, db, producer, avatars
from app.forms import LoginForm, RegistrationForm, RestorePasswordForm
from app.forms import EditAvatarForm, EditProfileForm, EditPasswordForm
from app.forms import InputProblemForm, FileProblemForm
from app.models import User, Contest, Problem, ContestRequest, Submission


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('413.html'), 413


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html', title='About')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('contests_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', category='alert-danger')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('contests_page'))
    return render_template('login.html', title='Sign in', active='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('contests_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered!', category='alert-success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', active='register', form=form)


@app.route('/restore', methods=['GET', 'POST'])
def restore_password():
    form = RestorePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username', category='alert-danger')
            return redirect(url_for('restore_password'))
        print('KEK')
    return render_template('restore.html', title='Restore password', form=form)


@app.route('/user/<username>')
def profile_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    avatar_form = EditAvatarForm()
    profile_form = EditProfileForm(user.email)
    password_form = EditPasswordForm()
    return render_template('user.html', title='View profile', user=user, 
        avatar_form=avatar_form, profile_form=profile_form, password_form=password_form)


@app.route('/avatars/<filename>')
def avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@app.route('/changeAvatar', methods=['POST'])
@login_required
def change_avatar():
    form = EditAvatarForm()
    if form.validate_on_submit():
        filename = avatars.save_avatar(form.image.data)
        current_user.avatar = filename
        db.session.commit()
        flash('Сохранено', category='alert-success')
    else:
        flash('Введённые данные некорректны', category='alert-danger')
    return redirect(url_for('profile_page', username=current_user.username))


@app.route('/changeProfile', methods=['POST'])
@login_required
def change_profile():
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.fullname = form.fullname.data
        current_user.birthdate = form.birthdate.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Сохранено', category='alert-success')
    else:
        flash('Введённые данные некорректны', category='alert-danger')
    return redirect(url_for('profile_page', username=current_user.username))


@app.route('/changePassword', methods=['POST'])
@login_required
def change_password():
    form = EditPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Неверный старый пароль', category='alert-danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменён', category='alert-success')
    else:
        flash('Введённые данные некорректны', category='alert-danger')
    return redirect(url_for('profile_page', username=current_user.username))


def get_contest_by_url(contest_url):
    contest_name = unquote_plus(contest_url)
    return Contest.query.filter_by(name=contest_name).first_or_404()


def get_contest_request(contest):
    return ContestRequest.query.filter_by(contest_id=contest.id, user_id=current_user.id).first()


@app.route('/contests')
@login_required
def contests_page():
    full_contests = [(contest, get_contest_request(contest)) for contest in Contest.query.all()]
    return render_template('contests.html', title='Contests', active='contests', contests=full_contests)


@app.route('/contests/<contest_url>/<number>')
@login_required
def contest_page(contest_url, number):
    contest = get_contest_by_url(contest_url)
    contest_request = get_contest_request(contest)
    problem = Problem.query.filter_by(contest=contest, number=number).first_or_404()
    submissions = Submission.query.filter_by(problem=problem, user=current_user).order_by(Submission.time.desc())
    if contest_request is None:
        flash('Недопустимая операция', category='alert-danger')
        return redirect(url_for('contests_page'))
    if contest_request.state() == 'Finished':
        flash('Ваше участие в контесте завершено', category='alert-info')
    problem_form = {}
    if problem.problem_type == 'Programming':
        problem_form = FileProblemForm(language=current_user.active_language)
    elif problem.problem_type == 'Test':
        problem_form = InputProblemForm()
    return render_template('contest.html', title=contest.name, contest_url=contest_url,
        contest=contest, problem=problem, request=contest_request, submissions=submissions, 
        form=problem_form)


def judge_submisssion(submission_id):
    producer.send('judge', value={'id': submission_id})


@app.route('/download/submission/<submission_id>')
@login_required
def download_submission(submission_id):
    submission = Submission.query.filter_by(id=submission_id).first_or_404()
    if submission.user != current_user:
        flash('Недопустимая операция', category='alert-danger')
        return redirect(url_for('contests_page'))
    source = submission.source
    download_folder = app.config['SUBMISSIONS_DOWNLOAD_PATH']
    filename = str(submission_id).zfill(6) + '.' + submission.language
    path = os.path.join(download_folder, filename)
    open(path, 'w').write(source)
    return send_from_directory(download_folder, filename, as_attachment=True)


@app.route('/contests/<contest_url>/<number>/send', methods=['POST'])
@login_required
def send(contest_url, number):
    contest = get_contest_by_url(contest_url)
    contest_request = get_contest_request(contest)
    problem = Problem.query.filter_by(contest=contest, number=number).first_or_404()
    try:
        if contest_request is None or contest_request.state() != 'In progress':
            raise ValueError('You are not allowed to send submissions in this contest')
        if problem.problem_type == 'Programming':
            problem_form = FileProblemForm()
            if not problem_form.validate_on_submit():
                raise ValueError('Form is not valid')
            language = problem_form.language.data
            source = problem_form.source.data.read().decode('utf-8')
            current_time = datetime.now().replace(microsecond=0)
            submission = Submission(contest=contest, problem=problem, user=current_user, time=current_time, 
                language=language, status='In queue', score=0, source=source)
            current_user.active_language = language
            db.session.add(submission)
            db.session.commit()
            judge_submisssion(submission.id)
            flash('Решение успешно отправлено', category='alert-success')
    except ValueError as error:
        flash('Ошибка отправки: ' + str(error), category='alert-danger')
    return redirect(url_for('contest_page', contest_url=contest_url, number=number))


@app.route('/contests/<contest_url>/start')
@login_required
def start_contest(contest_url):
    contest = get_contest_by_url(contest_url)
    contest_request = get_contest_request(contest)
    if contest_request is not None:
        flash('Недопустимая операция', category='alert-danger')
        return redirect(url_for('contests_page'))
    contest_request = ContestRequest(contest=contest, user=current_user, 
        start_time=datetime.now().replace(microsecond=0))
    db.session.commit()
    return redirect(url_for('contest_page', contest_url=contest_url, number=1))


@app.route('/contests/<contest_url>/finish')
@login_required
def finish_contest(contest_url):
    contest = get_contest_by_url(contest_url)
    contest_request = get_contest_request(contest)
    if contest_request is None or contest_request.state() in ['Not started', 'Finished']:
        flash('Недопустимая операция', category='alert-danger')
        return redirect(url_for('contests_page'))
    current_time = datetime.now().replace(microsecond=0)
    contest_request.finish_time = current_time
    db.session.commit()
    return redirect(url_for('contest_page', contest_url=contest_url, number=1))

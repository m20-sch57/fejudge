import os

from functools import wraps
from flask import render_template, jsonify, send_from_directory,\
    request, redirect, abort, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import UploadPackageForm # Remove then!
from app.events import send_new_submission_event
from app.services import register_user, create_contest_request, create_submission, create_problem,\
    get_user_by_username, get_contest_by_id_or_404, get_contest_request, get_contests_for_user,\
    get_problem_by_number_or_404, get_submission_by_id, get_submissions_by_problem_user,\
    evaluate_submission, initialize_problem
from app.verify import verify_login, verify_register, verify_submit


@app.errorhandler(403)
def resource_forbidden(error):
    return render_template(
        'error.html', page='error', message='Resource is forbidden.', code=403), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        'error.html', page='error', message='Oops! Page not found.', code=404), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template(
        'error.html', page='error', message='Method not allowed.', code=405), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template(
        'error.html', page='error', message='File is too large.', code=413), 413


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template(
        'error.html', page='error', message='Oops! Internal server error.', code=500), 500


@app.route('/')
@app.route('/welcome')
def welcome():
    return redirect(url_for('contests_page'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('contests_page'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not verify_login(username, password):
            return redirect(url_for('login'))
        user = get_user_by_username(username)
        login_user(user)
        return redirect(url_for('contests_page'))
    return render_template('login.html', page='login')


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
        if not verify_register(username, email, password):
            return redirect(url_for('register'))
        register_user(username, email, password)
        flash('You have successfully registered', category='success auto-dismiss')
        return redirect(url_for('login'))
    return render_template('register.html', page='register')


@app.route('/contests')
@login_required
def contests_page():
    return render_template(
        'contests.html', page='contests', contests=get_contests_for_user(current_user))


@app.route('/contests/<contest_id>')
@login_required
def contest_page(contest_id):
    contest = get_contest_by_id_or_404(contest_id)
    contest_request = get_contest_request(contest, current_user)
    if contest_request is None:
        return render_template('contest_register.html', page='contest_register', contest=contest)
    if contest_request.state() == 'Not started':
        return render_template('contest_wait.html', page='contest_wait')
    return redirect(url_for('contest_problem', contest_id=contest_id, number=1))


@app.route('/contests/<contest_id>/participate')
@login_required
def participate(contest_id):
    contest = get_contest_by_id_or_404(contest_id)
    contest_request = get_contest_request(contest, current_user)
    if contest_request is not None:
        flash('You are already participating in the contest', category='failure')
        return redirect(url_for('contests_page'))
    create_contest_request(contest=contest, user=current_user)
    return redirect(url_for('contest_problem', contest_id=contest.id, number=1))


def participation_required(func):
    @wraps(func)
    def decorated_view(contest_id, *args, **kwargs):
        contest = get_contest_by_id_or_404(contest_id)
        contest_request = get_contest_request(contest, current_user)
        if contest_request is None or contest_request.state() == 'Not started':
            abort(403)
        return func(contest_id, *args, **kwargs)
    return decorated_view


@app.route('/contests/<contest_id>/<number>/problem')
@login_required
@participation_required
def contest_problem(contest_id, number):
    contest = get_contest_by_id_or_404(contest_id)
    contest_request = get_contest_request(contest, current_user)
    problem = get_problem_by_number_or_404(contest, number)
    from invoker.problem_manage import ProblemManager
    problem_manager = ProblemManager(problem.id)
    return render_template(
        'problem.html',
        page='problem',
        contest=contest,
        contest_request=contest_request,
        problem=problem,
        problem_manager=problem_manager
    )


@app.route('/contests/<contest_id>/<number>/submit', methods=['POST'])
@login_required
@participation_required
def submit_problem(contest_id, number):
    contest = get_contest_by_id_or_404(contest_id)
    contest_request = get_contest_request(contest, current_user)
    problem = get_problem_by_number_or_404(contest, number)
    source_blob = request.files['sourceFile'].read()
    language = request.form['language']
    verify_submit(source_blob, language)
    source_code = source_blob.decode('utf-8')
    submission = create_submission(
        contest=contest,
        problem=problem,
        user=current_user,
        language=language,
        source=source_code
    )
    evaluate_submission(submission)
    send_new_submission_event(submission)
    return ''


@app.route('/contests/<contest_id>/<number>/submissions')
@login_required
@participation_required
def problem_submissions(contest_id, number):
    contest = get_contest_by_id_or_404(contest_id)
    problem = get_problem_by_number_or_404(contest, number)
    submissions = get_submissions_by_problem_user(problem, current_user)
    return jsonify([{
        'submission_id': submission.id,
        'submission_language': submission.language,
        'submission_status': submission.status,
        'submission_score': submission.score
    } for submission in submissions])


@app.route('/contests/<contest_id>/<number>/<resource>')
@login_required
@participation_required
def problem_resource(contest_id, number, resource):
    contest = get_contest_by_id_or_404(contest_id)
    problem = get_problem_by_number_or_404(contest, number)
    from invoker.problem_manage import ProblemManager
    problem_manager = ProblemManager(problem.id)
    resource_dir = None
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


@app.route('/submissions/<submission_id>/details')
@login_required
def submission_details(submission_id):
    submission = get_submission_by_id(submission_id)
    if not submission or submission.user != current_user:
        abort(403)
    return jsonify({
        'protocol': submission.get_protocol(),
        'source': submission.source,
        'user': submission.user.username,
        'language': submission.language,
        'time': submission.time,
        'status': submission.status,
        'score': submission.score
    })


def contest_admin(func):
    @wraps(func)
    def decorated_view(contest_id, *args, **kwargs):
        contest = get_contest_by_id_or_404(contest_id)
        if contest.owner != current_user:
            flash('You do not have admin privileges', category='alert-danger')
            return redirect(url_for('contests_page'))
        return func(contest_id, *args, **kwargs)
    return decorated_view


@app.route('/contests/<contest_id>/admin/newproblem', methods=['GET', 'POST'])
@login_required
@contest_admin
def contest_admin_newproblem(contest_id):
    contest = get_contest_by_id_or_404(contest_id)
    upload_package_form = UploadPackageForm()
    if upload_package_form.validate_on_submit():
        new_problem = create_problem(contest=contest, problem_type='prog')
        path = os.path.join(app.config['PROBLEMS_UPLOAD_PATH'], str(new_problem.id) + '.zip')
        upload_package_form.package.data.save(path)
        initialize_problem(new_problem)
        flash('Your package has been uploaded', category='alert-info')
        return redirect(url_for('contest_admin_newproblem', contest_id=contest_id))
    return render_template(
        'old/contest_admin_newproblem.html',
        title='New problem',
        contest=contest, 
        form=upload_package_form
    )

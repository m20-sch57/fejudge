import os
import shutil
import json
import datetime

from kafka import KafkaProducer, KafkaConsumer

import constants
from libsbox import Libsbox
from config import Config


def write_file(path, data):
    if type(data) is str:
        fout = open(path, 'w')
    elif type(data) is bytes:
        fout = open(path, 'wb')
    else:
        fout = None
    fout.write(data)
    fout.close()


def clear_submission(items_to_stay=[]):
    for item in os.listdir(Config.SUBMISSION_DIR):
        if item not in items_to_stay:
            os.remove(os.path.join(Config.SUBMISSION_DIR, item))


def parse_status(response, obj):
    task_response = response['tasks'][0]
    task_obj = obj['tasks'][0]
    if task_response['time_usage_ms'] >= task_obj['time_limit_ms']:
        return 'TL'
    if task_response['wall_time_usage_ms'] >= task_obj['wall_time_limit_ms']:
        return 'IL'
    if task_response['memory_limit_hit'] or task_response['oom_killed']:
        return 'ML'
    if task_response['exit_code'] != 0:
        return 'RE'
    return 'OK'


def parse_checker_status(response):
    exit_code = response['tasks'][0]['exit_code']
    if exit_code == 0:
        return 'OK'
    if exit_code == 1:
        return 'WA'
    if exit_code == 2:
        return 'PE'
    return 'FAIL'


def calc_test_maxscore(problem_maxscore, tests_cnt, test_num):
    rest = problem_maxscore % tests_cnt
    if test_num == tests_cnt - rest + 1:
        return problem_maxscore // tests_cnt + 1
    else:
        return problem_maxscore // tests_cnt


consumer = KafkaConsumer(
    'judge',
    bootstrap_servers=[Config.KAFKA_SERVER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    auto_commit_interval_ms=2000,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(0, 10)
)


if not os.path.exists(Config.SUBMISSION_DIR):
    os.makedirs(Config.SUBMISSION_DIR)
    # os.chmod(submission_dir, 0o755)
clear_submission()


for message in consumer:
    # submission = Submission.query.filter_by(id=int(message.value['id'])).first()
    submission = message.value['submission']
    problem = message.value['problem']
    # problem = submission.problem
    submission_details = {'tests': [], 'compiler': ''}

    # Submission paths
    # submission_dir = os.path.join(app.config['SUBMISSIONS_EXEC_PATH'], str(submission.id).zfill(6))

    submission_file = os.path.join(Config.SUBMISSION_DIR, 'participant.' + submission['language'])
    submission_program = os.path.join(Config.SUBMISSION_DIR, 'participant.out')
    # submission_checker_program = os.path.join(submission_dir, 'checker.out')
    # submission_input = os.path.join(submission_dir, 'input.txt')
    # submission_output = os.path.join(submission_dir, 'output.txt')
    # submission_answer = os.path.join(submission_dir, 'answer.txt')
    # submission_result = os.path.join(submission_dir, 'result.txt')
    # submission_error = os.path.join(submission_dir, 'error.txt')
    # submission_log = os.path.join(app.config['SUBMISSIONS_LOG_PATH'], str(submission.id).zfill(6))

    # Problem paths
    # problem_dir = os.path.join(app.config['PROBLEMS_PATH'], str(problem.id).zfill(6))
    # problem_input = os.path.join(problem_dir, 'input')
    # problem_output = os.path.join(problem_dir, 'output')
    # problem_checker_program = os.path.join(problem_dir, 'checker.out')

    # Prepare to compile solution
    # submission.status = 'Compiling'
    # db.session.commit()
    
    write_file(submission_file, submission['source'])
    # open(submission_file, 'w').write(submission['source'])
    # os.chmod(submission_file, 0o666)
    write_file(submission_program, b'')
    # open(submission_program, 'w').close()
    # os.chmod(submission_program, 0o777)
    write_file(Config.SUBMISSION_ERROR, '')
    # open(submission_error, 'w').close()
    # os.chmod(submission_error, 0o666)
    # log = open(submission_log, 'w')
    # os.chmod(submission_log, 0o666)

    # print('Started judging at {}\n\nProblem ID: {}\nLanguage: {}\nUser ID: {}\n'.format(
    #     datetime.datetime.utcnow(),
    #     submission.problem.id,
    #     submission.language,
    #     submission.user.id
    # ), file=log)

    # Compile solution
    compile_object = Libsbox.build_object(
        argv=constants.COMPILE_ARGV[submission['language']],
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=10000,
        memory_limit_kb=262144,
        max_threads=10,
        stdout='error.txt',
        stderr='@_stdout'
    )
    compile_response = json.loads(Libsbox.send(compile_object))
    compile_task = compile_response['tasks'][0]
    submission_details['compiler'] = open(Config.SUBMISSION_ERROR).read()
    # print('Compilation code: {}\nCompilation output:\n{}\n\n'.format(
    #     compile_task['exit_code'],
    #     submission_details['compiler']
    # ), file=log)
    if compile_task['exit_code'] != 0:
        print('compilation error')
        # submission.status = 'CE'
        # submission.set_details(submission_details)
        # print('Submission status: {}\nSubmission score: {}\n'.format(
        #     submission.status,
        #     submission.score
        # ), file=log)
        # log.close()
        # db.session.commit()
        continue

    # Running on tests
    # submission.status = 'Running'
    # db.session.commit()

    print('Compilation succeeded')
    raise ValueError
    print(open(submission_file).read())
    tests_list = sorted(os.listdir(problem_input))
    total_score = 0
    for it, test_str in enumerate(tests_list):
        test_maxscore = calc_test_maxscore(problem.max_score, len(tests_list), it + 1)

        # Current test input and output files
        test_input = os.path.join(problem_input, test_str)
        test_output = os.path.join(problem_output, test_str + '.a')

        # Clear container
        for item in os.listdir(submission_dir):
            if item not in ['participant.out']:
                os.remove(os.path.join(submission_dir, item))

        # Prepare to run submission
        shutil.copyfile(test_input, submission_input)
        open(submission_output, 'w').close()
        os.chmod(submission_output, 0o666)
        open(submission_error, 'w').close()
        os.chmod(submission_error, 0o666)

        # Run submission in container
        submission_obj = build_object(
            argv=constants.RUN_ARGV[submission.language],
            work_dir=submission_dir,
            time_limit_ms=1000,
            memory_limit_kb=262144,
            stdin='input.txt',
            stdout='output.txt',
            stderr='error.txt'
        )
        submission_response = json.loads(send_to_libsbox(submission_obj))
        submission_status = parse_status(submission_response, submission_obj)

        # Prepare to check answer
        shutil.copyfile(test_input, submission_input)
        os.chmod(submission_input, 0o666)
        shutil.copyfile(test_output, submission_answer)
        os.chmod(submission_answer, 0o666)
        open(submission_result, 'w').close()
        os.chmod(submission_result, 0o666)
        shutil.copyfile(problem_checker_program, submission_checker_program)
        os.chmod(submission_checker_program, 0o777)

        # Check answer in container
        checker_obj = build_object(
            argv=['./checker.out', 'input.txt', 'output.txt', 'answer.txt', 'result.txt'],
            work_dir=submission_dir,
            time_limit_ms=1000,
            memory_limit_kb=262144
        )
        checker_response = json.loads(send_to_libsbox(checker_obj))
        checker_status = parse_status(checker_response, checker_obj)

        if checker_status not in ['OK', 'RE']:
            submission_status = 'FAIL'
        if submission_status == 'OK':
            submission_status = parse_checker_status(checker_response)

        if submission_status == 'OK':
            test_score = test_maxscore
        else:
            test_score = 0
        total_score += test_score

        # Logging
        submission_task = submission_response['tasks'][0]
        test_details = {
            'status': submission_status,
            'time_usage_s': submission_task['time_usage_ms'] / 1000,
            'wall_time_usage_s': submission_task['wall_time_usage_ms'] / 1000,
            'memory_usage_kb': submission_task['memory_usage_kb'],
            'score': test_score,
            'maxscore': test_maxscore
        }
        submission_details['tests'].append(test_details)
        print('===== Test #{}, execution time: {}ms, memory used: {}kb =====\n'.format(
            it + 1,
            submission_task['time_usage_ms'],
            submission_task['memory_usage_kb']
        ), file=log)
        print('Input data:\n{}'.format(open(submission_input).read()[:1000]), file=log)
        print('Solution output data:\n{}'.format(open(submission_output).read()[:1000]), file=log)
        print('Correct answer:\n{}'.format(open(submission_answer).read()[:1000]), file=log)
        print('Error stream:\n{}'.format(open(submission_error).read()), file=log)
        print('Checker comments:\n{} {}\n\n'.format(
            submission_status,
            open(submission_result).read()
        ), file=log)

    submission.status = 'Accepted' if total_score == problem.max_score else 'Partial'
    submission.score = total_score
    submission.set_details(submission_details)
    print('Submission status: {}\nSubmission score: {}\n'.format(
        submission.status,
        submission.score
    ), file=log)
    log.close()
    db.session.commit()

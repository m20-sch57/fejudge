import os
import shutil
import json
import time
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from kafka import KafkaConsumer

import constants
from libsbox import Libsbox
from config import Config
from models import Base, Submission


def read_file(path):
    return open(path, 'r').read()


def write_file(path, data=''):
    fout = open(path, 'w')
    fout.write(data)
    fout.close()


def number_of_tests(problem_id):
    return len(os.listdir(os.path.join(Config.PROBLEMS_PATH, str(problem_id).zfill(6), 'input')))


def write_logs(submission_id, data):
    path = os.path.join(
        Config.SUBMISSIONS_LOG_PATH,
        str(submission_id).zfill(6) + '.txt'
    )
    open(path, 'a').write(data)


def set_submission_status(submission_id, status, score=0, details=None):
    submission = session.query(Submission).filter_by(id=submission_id).first()
    if submission is None:
        return
    submission.status = status
    submission.score = score
    if details is not None:
        submission.details = json.dumps(details)
    session.commit()


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


def run_on_test(test_number):
    test_input_file = os.path.join(
        Config.PROBLEMS_PATH, str(problem['id']).zfill(6), 'input', str(test_number).zfill(3)
    )
    test_output_file = os.path.join(
        Config.PROBLEMS_PATH, str(problem['id']).zfill(6), 'output', str(test_number).zfill(3) + '.a'
    )
    checker_file = os.path.join(
        Config.PROBLEMS_PATH, str(problem['id']).zfill(6), Config.SUBMISSION_CHECKER_NAME
    )

    clear_submission(items_to_stay=['participant.out'])
    shutil.copyfile(test_input_file, Config.SUBMISSION_INPUT)
    write_file(Config.SUBMISSION_OUTPUT)
    write_file(Config.SUBMISSION_ERROR)

    submission_object = libsbox.build_object(
        argv=constants.RUN_ARGV[submission['language']],
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=problem['time_limit_ms'],
        memory_limit_kb=problem['memory_limit_kb'],
        stdin=Config.SUBMISSION_INPUT_NAME,
        stdout=Config.SUBMISSION_OUTPUT_NAME,
        stderr=Config.SUBMISSION_ERROR_NAME
    )
    submission_response = json.loads(libsbox.send(submission_object))
    test_status = parse_status(submission_response, submission_object)

    shutil.copyfile(checker_file, Config.SUBMISSION_CHECKER)
    shutil.copyfile(test_input_file, Config.SUBMISSION_INPUT)
    shutil.copyfile(test_output_file, Config.SUBMISSION_ANSWER)
    write_file(Config.SUBMISSION_RESULT)

    checker_object = libsbox.build_object(
        argv=[
            './' + Config.SUBMISSION_CHECKER_NAME,
            Config.SUBMISSION_INPUT_NAME,
            Config.SUBMISSION_OUTPUT_NAME,
            Config.SUBMISSION_ANSWER_NAME,
            Config.SUBMISSION_RESULT_NAME
        ],
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=Config.CHECKER_TIME_LIMIT_MS,
        memory_limit_kb=Config.CHECKER_MEMORY_LIMIT_KB
    )
    checker_response = json.loads(libsbox.send(checker_object))
    checker_status = parse_status(checker_response, checker_object)
    if checker_status not in ['OK', 'RE']:
        test_status = 'FAIL'
    if test_status == 'OK':
        test_status = parse_checker_status(checker_response)

    submission_task = submission_response['tasks'][0]
    test_details = {
        'status': test_status,
        'time_usage_s': submission_task['time_usage_ms'] / 1000,
        'wall_time_usage_s': submission_task['wall_time_usage_ms'] / 1000,
        'memory_usage_kb': submission_task['memory_usage_kb']
    }
    write_logs(submission['id'], (
        '===== Test #{}, execution time: {}ms, memory used: {}kb =====\n'
        'Input data:\n{}\n'
        'Solution output data:\n{}\n'
        'Correct answer:\n{}\n'
        'Error stream:\n{}\n'
        'Checker comments:\n{} {}\n\n'
    ).format(
        test_number,
        submission_task['time_usage_ms'],
        submission_task['memory_usage_kb'],
        read_file(test_input_file),
        read_file(Config.SUBMISSION_OUTPUT),
        read_file(test_output_file),
        read_file(Config.SUBMISSION_ERROR),
        test_status,
        read_file(Config.SUBMISSION_RESULT)
    ))

    return (test_status, test_details)


def compile():
    submission_file = os.path.join(Config.SUBMISSION_DIR, 'participant.' + submission['language'])
    submission_program = os.path.join(Config.SUBMISSION_DIR, 'participant.out')

    write_file(submission_file, submission['source'])
    write_file(submission_program)
    write_file(Config.SUBMISSION_ERROR)
    write_logs(submission['id'],
        'Started judging at {}\n\nProblem ID: {}\nSubmission ID: {}\nLanguage: {}\n'.format(
            datetime.datetime.today().replace(microsecond=0),
            problem['id'],
            submission['id'],
            submission['language']
        )
    )
    
    set_submission_status(submission['id'], status='Compiling')
    # os.chmod(submission_program, 0o777)
    compile_object = libsbox.build_object(
        argv=constants.COMPILE_ARGV[submission['language']],
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=Config.SUBMISSION_ERROR_NAME,
        stderr='@_stdout'
    )
    compile_response = json.loads(libsbox.send(compile_object))
    compile_status = 'OK' if compile_response['tasks'][0]['exit_code'] == 0 else 'CE'
    compile_details = read_file(Config.SUBMISSION_ERROR)

    write_logs(submission['id'],
        'Compilation code: {}\nCompilation output:\n{}\n\n'.format(
            compile_response['tasks'][0]['exit_code'],
            compile_details
        )
    )

    return (compile_status, compile_details)


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
session = Session(bind=engine)

libsbox = Libsbox()
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
clear_submission()

for message in consumer:
    submission = message.value['submission']
    problem = message.value['problem']

    submission_status = ''
    submission_score = 0
    submission_details = {'tests': [], 'compiler': ''}

    submission_status, submission_details['compiler'] = compile()
    if submission_status == 'OK':
        set_submission_status(submission['id'], status='Running')
        tests_cnt = number_of_tests(problem['id'])
        total_score = 0
        for test_number in range(1, tests_cnt + 1):
            test_status, test_details = run_on_test(test_number)
            test_maxscore = calc_test_maxscore(problem['max_score'], tests_cnt, test_number)
            test_score = test_maxscore if test_status == 'OK' else 0
            test_details['score'] = test_score
            test_details['maxscore'] = test_maxscore
            total_score += test_score
            submission_details['tests'].append(test_details)
        submission_status = 'Accepted' if total_score == problem['max_score'] else 'Partial'
        submission_score = total_score

    set_submission_status(submission['id'], status=submission_status, score=submission_score, details=submission_details)
    write_logs(submission['id'],
        'Submission status: {}\nSubmission score: {}\n'.format(
            submission_status,
            submission_score
        )
    )

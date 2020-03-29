import os
import sys
import shutil
import json
import time
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from kafka import KafkaConsumer

import constants
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from libsbox.client import Libsbox
from packagemanager import ProblemManager
from submission import SubmissionManager
from config import Config
from models import Base, Submission


def read_file(path):
    return open(path, 'r').read()


def write_file(path, data=''):
    fout = open(path, 'w')
    fout.write(data)
    fout.close()


def parse_execution_status(response, obj):
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


def calc_test_maxscore(problem_maxscore, tests_cnt, test_number):
    rest = problem_maxscore % tests_cnt
    if test_number >= tests_cnt - rest + 1:
        return problem_maxscore // tests_cnt + 1
    else:
        return problem_maxscore // tests_cnt


def run_on_test(test_number, submission_manager, problem_manager):
    submission_manager.clear_data(items_to_stay=['participant.out'])
    shutil.copyfile(problem_manager.test_input_file(test_number), submission_manager.input_file)
    write_file(submission_manager.output_file)
    write_file(submission_manager.error_file)
    submission_object = libsbox.build_object(
        argv=submission_manager.run_argv,
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=problem_manager.time_limit_ms,
        memory_limit_kb=problem_manager.memory_limit_kb,
        stdin='input.txt',
        stdout='output.txt',
        stderr='error.txt'
    )
    submission_response = json.loads(libsbox.send(submission_object))
    test_status = parse_execution_status(submission_response, submission_object)
    shutil.copyfile(problem_manager.checker_binary, submission_manager.checker_binary)
    shutil.copyfile(problem_manager.test_input_file(test_number), submission_manager.input_file)
    shutil.copyfile(problem_manager.test_output_file(test_number), submission_manager.answer_file)
    write_file(submission_manager.result_file)
    os.chmod(submission_manager.checker_binary, 0o777)
    os.chmod(submission_manager.result_file, 0o777)
    checker_object = libsbox.build_object(
        argv=submission_manager.checker_argv,
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=Config.CHECKER_TIME_LIMIT_MS,
        memory_limit_kb=Config.CHECKER_MEMORY_LIMIT_KB
    )
    checker_response = json.loads(libsbox.send(checker_object))
    checker_status = parse_execution_status(checker_response, checker_object)
    test_status = 'FAIL' if checker_status not in ['OK', 'RE'] else test_status
    test_status = parse_checker_status(checker_response) if test_status == 'OK' else test_status
    submission_task = submission_response['tasks'][0]
    test_details = {
        'status': test_status,
        'time_usage_s': submission_task['time_usage_ms'] / 1000,
        'wall_time_usage_s': submission_task['wall_time_usage_ms'] / 1000,
        'memory_usage_kb': submission_task['memory_usage_kb']
    }
    submission_manager.write_logs((
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
        read_file(problem_manager.test_input_file(test_number)),
        read_file(submission_manager.output_file),
        read_file(problem_manager.test_output_file(test_number)),
        read_file(submission_manager.error_file),
        test_status,
        read_file(submission_manager.result_file)
    ))
    return (test_status, test_details)


def compile(submission_manager):
    submission_manager.clear_data()
    write_file(submission_manager.participant_source, submission_manager.submission.source)
    write_file(submission_manager.participant_binary)
    write_file(submission_manager.error_file)
    os.chmod(submission_manager.participant_binary, 0o777)
    compile_object = libsbox.build_object(
        argv=submission_manager.compile_argv,
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout='error.txt',
        stderr='@_stdout'
    )
    compile_response = json.loads(libsbox.send(compile_object))
    compile_status = 'OK' if compile_response['tasks'][0]['exit_code'] == 0 else 'CE'
    compile_details = read_file(submission_manager.error_file)
    compile_task = compile_response['tasks'][0]
    submission_manager.write_logs(
        'Compilation code: {}\nCompilation output:\n{}\n\n'.format(
            compile_task['exit_code'],
            compile_details
        )
    )
    return (compile_status, compile_details)


def evaluate(submission_id):
    print('Started evaluating submission', submission_id, flush=True)
    submission = session.query(Submission).filter_by(id=submission_id).first()
    if submission is None:
        print('Cannot find submission', submission_id, flush=True)
        return
    submission_manager = SubmissionManager(submission)
    problem_manager = ProblemManager(submission.problem_id)
    submission_manager.write_logs(
        'Started judging at {}\n\nProblem ID: {}\nSubmission ID: {}\nLanguage: {}\n'.format(
            datetime.datetime.today().replace(microsecond=0),
            submission_manager.problem.id,
            submission_manager.submission.id,
            submission_manager.submission.language
        )
    )
    submission.status = 'Compiling'
    submission.score = 0
    session.commit()
    compile_status, compile_details = compile(submission_manager)
    submission_details = {'tests': [], 'compiler': compile_details}
    if compile_status == 'OK':
        submission.status = 'Running'
        session.commit()
        for test_number in range(1, problem_manager.number_of_tests() + 1):
            test_status, test_details = run_on_test(test_number, submission_manager, problem_manager)
            test_maxscore = calc_test_maxscore(
                submission.problem.max_score, problem_manager.number_of_tests(), test_number) # TODO: valuer
            test_score = test_maxscore if test_status == 'OK' else 0
            test_details['score'] = test_score
            test_details['maxscore'] = test_maxscore
            submission.score += test_score
            submission_details['tests'].append(test_details)
        submission.status = 'Accepted' if submission.score == submission.problem.max_score else 'Partial'
    else:
        submission.status = 'Compilation error'
    submission.details = json.dumps(submission_details)
    session.commit()
    submission_manager.write_logs(
        'Submission status: {}\nSubmission score: {}\n'.format(
            submission.status,
            submission.score
        )
    )
    print('Finished evaluating submission', submission_id, flush=True)


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
session = Session(bind=engine)

libsbox = Libsbox()
consumer = KafkaConsumer(
    'judge',
    bootstrap_servers=[Config.KAFKA_SERVER],
    auto_offset_reset='earliest',
    session_timeout_ms=120000, # maximum time to judge one submission
    max_poll_records=1,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(0, 10)
)

if not os.path.exists(Config.SUBMISSION_DIR):
    os.makedirs(Config.SUBMISSION_DIR)

for message in consumer:
    evaluate(message.value['submission_id'])

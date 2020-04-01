import os
import sys
import shutil
import json
import time
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from kafka import KafkaConsumer

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from libsbox.client import Libsbox
from packagemanager import ProblemManager
from config import Config
from models import Base, Submission


def read_file(path):
    return open(path, 'r').read()


def write_file(path, data=''):
    fout = open(path, 'w')
    fout.write(data)
    fout.close()


def write_logs(submission_id, message):
    fout = open(os.path.join(Config.SUBMISSIONS_LOG_PATH, str(submission_id).zfill(6) + '.txt'), 'a')
    fout.write(message)
    fout.close()


def clear_submission_dir(items_to_stay=[]):
    for item in os.listdir(Config.SUBMISSION_DIR):
        if item not in items_to_stay:
            os.remove(os.path.join(Config.SUBMISSION_DIR, item))


def calc_test_maxscore(problem_maxscore, tests_cnt, test_number):
    rest = problem_maxscore % tests_cnt
    if test_number >= tests_cnt - rest + 1:
        return problem_maxscore // tests_cnt + 1
    else:
        return problem_maxscore // tests_cnt


def run_on_test(test_number, submission, problem_manager):
    clear_submission_dir(items_to_stay=[Config.PARTICIPANT_BINARY_RELPATH])
    shutil.copyfile(problem_manager.test_input_path(test_number), Config.INPUT_PATH)
    write_file(Config.OUTPUT_PATH)
    write_file(Config.ERROR_PATH)
    submission_object = libsbox.build_object(
        argv=libsbox.get_run_argv(
            filename=Config.PARTICIPANT_BINARY_RELPATH,
            language=submission.language
        ),
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=problem_manager.time_limit_ms,
        memory_limit_kb=problem_manager.memory_limit_kb,
        stdin=Config.INPUT_RELPATH,
        stdout=Config.OUTPUT_RELPATH,
        stderr=Config.ERROR_RELPATH
    )
    submission_response = json.loads(libsbox.send(submission_object))
    test_status = libsbox.parse_execution_status(submission_response, submission_object)
    shutil.copyfile(problem_manager.checker_binary_path, Config.CHECKER_BINARY_PATH)
    shutil.copyfile(problem_manager.test_input_path(test_number), Config.INPUT_PATH)
    shutil.copyfile(problem_manager.test_output_path(test_number), Config.ANSWER_PATH)
    write_file(Config.RESULT_PATH)
    os.chmod(Config.CHECKER_BINARY_PATH, 0o777)
    os.chmod(Config.RESULT_PATH, 0o777)
    checker_object = libsbox.build_object(
        argv=libsbox.get_run_argv(
            filename=Config.CHECKER_BINARY_RELPATH,
            language=problem_manager.checker_language,
            additional_argv=[
                Config.INPUT_RELPATH,
                Config.OUTPUT_RELPATH,
                Config.ANSWER_RELPATH,
                Config.RESULT_RELPATH
            ]
        ),
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=Config.CHECKER_TIME_LIMIT_MS,
        memory_limit_kb=Config.CHECKER_MEMORY_LIMIT_KB
    )
    checker_response = json.loads(libsbox.send(checker_object))
    checker_status = libsbox.parse_execution_status(checker_response, checker_object)
    test_status = 'FAIL' if checker_status not in ['OK', 'RE'] else test_status
    test_status = libsbox.parse_checker_status(checker_response) if test_status == 'OK' else test_status
    submission_task = submission_response['tasks'][0]
    test_details = {
        'status': test_status,
        'time_usage_s': submission_task['time_usage_ms'] / 1000,
        'wall_time_usage_s': submission_task['wall_time_usage_ms'] / 1000,
        'memory_usage_kb': submission_task['memory_usage_kb']
    }
    write_logs(submission.id, (
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
        read_file(problem_manager.test_input_path(test_number)),
        read_file(Config.OUTPUT_PATH),
        read_file(problem_manager.test_output_path(test_number)),
        read_file(Config.ERROR_PATH),
        test_status,
        read_file(Config.RESULT_PATH)
    ))
    return (test_status, test_details)


def compile(submission):
    clear_submission_dir()
    participant_source_relpath = libsbox.gen_source_filename(
        Config.PARTICIPANT_SOURCE_RELPATH, submission.language)
    participant_source_path = libsbox.gen_source_filename(
        Config.PARTICIPANT_SOURCE_PATH, submission.language)
    write_file(participant_source_path, submission.source)
    write_file(Config.PARTICIPANT_BINARY_PATH)
    write_file(Config.ERROR_PATH)
    os.chmod(Config.PARTICIPANT_BINARY_PATH, 0o777)
    compile_object = libsbox.build_object(
        argv=libsbox.get_compile_argv(
            filename=participant_source_relpath,
            language=submission.language,
            output=Config.PARTICIPANT_BINARY_RELPATH
        ),
        work_dir=Config.SUBMISSION_DIR,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=Config.ERROR_RELPATH,
        stderr='@_stdout'
    )
    compile_response = json.loads(libsbox.send(compile_object))
    compile_status = libsbox.parse_execution_status(compile_response, compile_object)
    compile_details = read_file(Config.ERROR_PATH)
    compile_task = compile_response['tasks'][0]
    write_logs(submission.id,
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
    problem_manager = ProblemManager(submission.problem_id)
    write_logs(submission_id,
        'Started judging at {}\n\nProblem ID: {}\nSubmission ID: {}\nLanguage: {}\n'.format(
            datetime.datetime.today().replace(microsecond=0),
            submission.problem_id,
            submission_id,
            submission.language
        )
    )
    submission.status = 'Compiling'
    submission.score = 0
    session.commit()
    compile_status, compile_details = compile(submission)
    submission_details = {'tests': [], 'compiler': compile_details}
    if compile_status == 'OK':
        submission.status = 'Running'
        session.commit()
        for test_number in range(1, problem_manager.test_count + 1):
            test_status, test_details = run_on_test(test_number, submission, problem_manager)
            test_maxscore = calc_test_maxscore(
                submission.problem.max_score, problem_manager.test_count, test_number) # TODO: valuer
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
    write_logs(submission_id,
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

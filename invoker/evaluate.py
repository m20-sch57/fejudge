import json

from libsbox_client import File, libsbox
from problem_manage import ProblemManager
from models import Submission
from config import Config


# def write_logs(submission_id, message):
#     fout = open(os.path.join(Config.SUBMISSIONS_LOG_PATH, str(submission_id).zfill(6) + '.txt'), 'a')
#     fout.write(message)
#     fout.close()


def parse_checker_status(exit_code):
    if exit_code == 0:
        return 'OK'
    if exit_code == 1:
        return 'WA'
    if exit_code == 2:
        return 'PE'
    return 'FAIL'


def run_on_test(test_number, binary_file, problem_manager):
    input_file = File(
        internal_path='input.txt',
        external_path=problem_manager.test_input_path(test_number)
    )
    answer_file = File(
        internal_path='answer.txt',
        external_path=problem_manager.test_output_path(test_number)
    )
    checker_file = File(
        language=problem_manager.checker_language,
        external_path=problem_manager.checker_binary_path
    )
    libsbox.clear(files_to_stay=[binary_file])
    libsbox.import_file(input_file)
    error_file = libsbox.create_file('error')
    output_file = libsbox.create_file('output')
    participant_status, participant_task = libsbox.run(binary_file,
        time_limit_ms=problem_manager.time_limit_ms,
        memory_limit_kb=problem_manager.memory_limit_kb,
        stdin=input_file.internal_path,
        stdout=output_file.internal_path,
        stderr=error_file.internal_path
    )
    libsbox.import_file(checker_file)
    libsbox.import_file(input_file)
    libsbox.import_file(answer_file)
    result_file = libsbox.create_file('result')
    checker_status, checker_task = libsbox.run(checker_file,
        additional_argv=[
            input_file.internal_path,
            output_file.internal_path,
            answer_file.internal_path,
            result_file.internal_path
        ],
        time_limit_ms=Config.CHECKER_EXECUTION_TIME_LIMIT_MS,
        memory_limit_kb=Config.CHECKER_EXECUTION_MEMORY_LIMIT_KB
    )
    checker_exit_code = checker_task['exit_code']
    test_status = participant_status if checker_status in ['OK', 'RE'] else 'FAIL'
    test_status = parse_checker_status(checker_exit_code) if test_status == 'OK' else test_status
    test_details = {
        'status': test_status,
        'time_usage_s': participant_task['time_usage_ms'] / 1000,
        'wall_time_usage_s': participant_task['wall_time_usage_ms'] / 1000,
        'memory_usage_kb': participant_task['memory_usage_kb']
    }
    return (test_status, test_details)
    # write_logs(submission.id, (
    #     '===== Test #{}, execution time: {}ms, memory used: {}kb =====\n'
    #     'Input data:\n{}\n'
    #     'Solution output data:\n{}\n'
    #     'Correct answer:\n{}\n'
    #     'Error stream:\n{}\n'
    #     'Checker comments:\n{} {}\n\n'
    # ).format(
    #     test_number,
    #     submission_task['time_usage_ms'],
    #     submission_task['memory_usage_kb'],
    #     read_file(problem_manager.test_input_path(test_number)),
    #     read_file(Config.OUTPUT_PATH),
    #     read_file(problem_manager.test_output_path(test_number)),
    #     read_file(Config.ERROR_PATH),
    #     test_status,
    #     read_file(Config.RESULT_PATH)
    # ))


def compile(submission):
    libsbox.clear()
    source_file = libsbox.create_file('participant', language=submission.language)
    error_file = libsbox.create_file('error')
    libsbox.write_file(source_file, submission.source)
    compile_status, compile_task, binary_file = libsbox.compile(source_file,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    compile_details = libsbox.read_file(error_file)
    return (compile_status, compile_details, binary_file)
    # write_logs(submission.id,
    #     'Compilation code: {}\nCompilation output:\n{}\n\n'.format(
    #         compile_task['exit_code'],
    #         compile_details
    #     )
    # )


def evaluate(submission_id, session, sio):
    print('Started evaluating submission {}'.format(submission_id), flush=True)
    submission = session.query(Submission).filter_by(id=submission_id).first()
    if submission is None:
        print('Cannot find submission {}'.format(submission_id), flush=True)
        return
    problem_manager = ProblemManager(submission.problem_id)
    # write_logs(submission_id,
    #     'Started judging at {}\n\nProblem ID: {}\nSubmission ID: {}\nLanguage: {}\n'.format(
    #         datetime.datetime.today().replace(microsecond=0),
    #         submission.problem_id,
    #         submission_id,
    #         submission.language
    #     )
    # )
    submission.status = 'compiling'
    submission.score = 0
    session.commit()
    sio.emit('compiling', submission_id)
    compile_status, compile_details, binary_file = compile(submission)
    submission_details = {'tests': [], 'compiler': compile_details}
    if compile_status == 'OK':
        submission.status = 'evaluating'
        session.commit()
        sio.emit('evaluating', submission_id)
        test_count = problem_manager.test_count
        submission_details['tests'] = [{'status': 'NO'}] * test_count
        current_score = submission.problem.max_score
        for test_number in range(test_count):
            test_status, test_details = run_on_test(test_number + 1, binary_file, problem_manager)
            submission_details['tests'][test_number] = test_details
            if test_status != 'OK': # TODO: valuer
                current_score = 0
                break
        submission.score = current_score
        submission.status = 'accepted' if current_score == submission.problem.max_score else 'partial'
    else:
        submission.score = 0
        submission.status = 'compilation_error'
    submission.set_details(submission_details)
    session.commit()
    sio.emit('completed', (submission_id, submission.status, submission.score))
    # write_logs(submission_id,
    #     'Submission status: {}\nSubmission score: {}\n'.format(
    #         submission.status,
    #         submission.score
    #     )
    # )
    print('Finished evaluating submission {}'.format(submission_id), flush=True)

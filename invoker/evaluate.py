from services import commit_session, get_submission_by_id,\
    send_compiling_event, send_evaluating_event, send_completed_event
from invoker import libsbox
from libsbox_client import File
from problem_manage import ProblemManager
from config import Config


class EvaluationError(Exception):
    def __init__(self, cause='', details=''):
        super(EvaluationError, self).__init__(cause)
        self.cause = cause
        self.details = details


def parse_checker_status(exit_code: int):
    if exit_code == 0:
        return 'OK'
    if exit_code == 1:
        return 'WA'
    if exit_code == 2:
        return 'PE'
    return 'FAIL'


def compile(submission):
    libsbox.clear()
    source_file = libsbox.create_file('participant', language=submission.language)
    error_file = libsbox.create_file('error')
    libsbox.write_file(source_file, submission.source)
    compilation_status, compilation_task, binary_file = libsbox.compile(source_file,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    compilation_details = libsbox.read_file(error_file)
    return (compilation_status, compilation_details, binary_file)
    # write_logs(submission.id,
    #     'Compilation code: {}\nCompilation output:\n{}\n\n'.format(
    #         compilation_task['exit_code'],
    #         compilation_details
    #     )
    # )


def run_on_test(test_number: int, binary_file: File, problem_manager: ProblemManager):
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


def check_dependencies(group: str, group_dependencies: list, failed_groups: set):
    for previous_group in group_dependencies:
        if previous_group in failed_groups:
            return False
    return True


def run_on_tests(binary_file: File, problem_manager: ProblemManager):
    evaluation_details = [{'status': 'NO'}] * problem_manager.test_count
    group_score = dict([(name, 0) for name in problem_manager.groups.keys()])
    failed_groups = set()
    for ind in problem_manager.test_order:
        test_number = problem_manager.tests[ind]['test_number']
        test_group = problem_manager.tests[ind]['group']
        test_points = problem_manager.tests[ind]['points']
        test_group_info = problem_manager.groups[test_group]
        if test_group in failed_groups:
            continue
        if not check_dependencies(test_group, test_group_info['dependencies'], failed_groups):
            failed_groups.add(test_group)
            continue
        test_status, test_details = run_on_test(test_number, binary_file, problem_manager)
        test_score = test_points if test_status == 'OK' else 0
        evaluation_details[ind] = {
            'status': test_status,
            'group': test_group,
            'score': test_score,
            'maxscore': test_points,
            **test_details
        }
        group_score[test_group] += test_score
        if test_status != 'OK' and test_group_info['points-policy'] == 'complete-group':
            group_score[test_group] = 0
            failed_groups.add(test_group)

    submission_status = 'AC'
    for ind in problem_manager.test_order:
        test_status = evaluation_details[ind]['status']
        if test_status != 'OK':
            submission_status = test_status if not problem_manager.test_points_enabled else 'PT'
            break
    submission_score = 0
    for score in group_score.values():
        submission_score += score
    if not problem_manager.test_points_enabled and submission_status == 'AC':
        submission_score = 100
    return evaluation_details, submission_status, submission_score


def evaluate(submission_id):
    submission = get_submission_by_id(submission_id)
    if submission is None:
        return
    problem_manager = ProblemManager(submission.problem_id)
    problem_manager.init_tests()
    submission.status = 'compiling'
    commit_session()
    send_compiling_event(submission_id)
    try:
        compilation_status, compilation_details, binary_file = compile(submission)
    except Exception as e:
        raise EvaluationError(
            cause='An exception has occurred during compiling the solution',
            details=str(e)
        )
    if compilation_status == 'OK':
        submission.status = 'evaluating'
        commit_session()
        send_evaluating_event(submission_id)
        try:
            evaluation_details, submission.status, submission.score = run_on_tests(binary_file, problem_manager)
        except Exception as e:
            raise EvaluationError(
                cause='An exception has occurred during running the solution',
                details=str(e)
            )
    else:
        evaluation_details = []
        submission.status = 'CE'
        submission.score = 0
    submission.set_protocol({
        'compilation': compilation_details,
        'evaluation': evaluation_details
    })
    commit_session()
    send_completed_event(submission_id)

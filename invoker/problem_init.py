import os

from zipfile import ZipFile
from services import commit_session, get_problem_by_id
from invoker import libsbox
from libsbox_client import File
from problem_manage import ProblemManager
from config import Config


class InitializationError(Exception):
    def __init__(self, cause='', details=''):
        super(InitializationError, self).__init__(cause)
        self.cause = cause
        self.details = details


def extract_archive(problem_id: int):
    archive_path = os.path.join(Config.PROBLEMS_UPLOAD_PATH, str(problem_id) + '.zip')
    problem_path = os.path.join(Config.PROBLEMS_PATH, str(problem_id))
    if not os.path.exists(archive_path):
        return False
    ZipFile(archive_path, 'r').extractall(problem_path)
    return True


def compile_checker(problem_manager: ProblemManager):
    checker_source_file = File(
        language=problem_manager.checker_language,
        external_path=problem_manager.checker_source_path
    )
    testlib_file = File(
        language='cpp',
        external_path=problem_manager.testlib_path
    )
    libsbox.clear()
    libsbox.import_file(checker_source_file)
    if problem_manager.checker_type == 'testlib':
        libsbox.import_file(testlib_file)
    error_file = libsbox.create_file('error')
    compilation_status, compilation_task, checker_binary_file = libsbox.compile(checker_source_file,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    if compilation_status != 'OK':
        raise InitializationError(
            cause='Failed to compile checker',
            details={
                'status': compilation_status,
                'errors': libsbox.read_file(error_file)
            }
        )
    checker_binary_file.external_path = problem_manager.checker_binary_path
    libsbox.export_file(checker_binary_file)


def compile_main_solution(problem_manager: ProblemManager):
    main_solution_source_file = File(
        language=problem_manager.main_solution_language,
        external_path=problem_manager.main_solution_source_path
    )
    libsbox.import_file(main_solution_source_file)
    error_file = libsbox.create_file('error')
    compilation_status, compilation_task, main_solution_binary_file = libsbox.compile(main_solution_source_file,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    if compilation_status != 'OK':
        raise InitializationError(
            cause='Failed to compile main solution',
            details={
                'status': compilation_status,
                'errors': libsbox.read_file(error_file)
            }
        )
    return main_solution_binary_file


def compile_executables(problem_manager: ProblemManager):
    executables_bin = []
    for executable in problem_manager.executables:
        executable_source_file = File(
            language=executable['language'],
            external_path=executable['path']
        )
        libsbox.import_file(executable_source_file)
        error_file = libsbox.create_file('error')
        compilation_status, compilation_task, executable_binary_file = libsbox.compile(executable_source_file,
            time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
            memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
            max_threads=10,
            stdout=error_file.internal_path,
            stderr='@_stdout'
        )
        if compilation_status != 'OK':
            raise InitializationError(
                cause='Failed to compile executable {}'.format(executable_source_file.internal_path),
                details={
                    'status': compilation_status,
                    'errors': libsbox.read_file(error_file)
                }
            )
        executables_bin.append(executable_binary_file)
    return executables_bin


def generate_tests(problem_manager: ProblemManager, main_solution_binary_file: File, executables_bin: list):
    for test_info in problem_manager.tests:
        test_number = test_info['test_number']
        input_file = libsbox.create_file('input')
        input_file.external_path = problem_manager.test_input_path(test_number)
        output_file = libsbox.create_file('output')
        output_file.external_path = problem_manager.test_output_path(test_number)
        error_file = libsbox.create_file('error')
        if test_info['generate_input']:
            program_name = test_info['program']
            additional_argv = test_info['additional_argv']
            executable = next(filter(lambda elem: elem.internal_path == program_name, executables_bin))
            generator_status, generator_task = libsbox.run(executable, additional_argv=additional_argv,
                time_limit_ms=Config.GENERATOR_EXECUTION_TIME_LIMIT_MS,
                memory_limit_kb=Config.GENERATOR_EXECUTION_MEMORY_LIMIT_KB,
                stdout=input_file.internal_path,
                stderr=error_file.internal_path
            )
            if generator_status != 'OK':
                raise InitializationError(
                    cause='Failed to generate input for test {}'.format(test_number),
                    details={
                        'status': generator_status,
                        'errors': libsbox.read_file(error_file)
                    }
                )
            libsbox.export_file(input_file)
        else:
            libsbox.import_file(input_file)
        if test_info['generate_output']:
            solution_status, solution_task = libsbox.run(main_solution_binary_file,
                time_limit_ms=problem_manager.time_limit_ms,
                memory_limit_kb=problem_manager.memory_limit_kb,
                stdin=input_file.internal_path,
                stdout=output_file.internal_path,
                stderr=error_file.internal_path
            )
            if solution_status != 'OK':
                raise InitializationError(
                    cause='Failed to generate output for test {}'.format(test_number),
                    details={
                        'status': solution_status,
                        'errors': libsbox.read_file(error_file)
                    }
                )
            libsbox.export_file(output_file)
        else:
            libsbox.import_file(output_file)


def init(problem_id: int):
    print('Started initializing problem {}'.format(problem_id))
    success = extract_archive(problem_id)
    if not success:
        raise InitializationError(cause='Failed to extract archive')
    try:
        problem_manager = ProblemManager(problem_id)
        problem_manager.init_tests()
    except Exception as e:
        raise InitializationError(cause='Problem package is invalid', details={'error': str(e)})
    print('Compiling checker...')
    compile_checker(problem_manager)
    print('Compiling main solution...')
    main_solution_binary_file = compile_main_solution(problem_manager)
    print('Compiling executables...')
    executables_bin = compile_executables(problem_manager)
    print('Generating tests...')
    generate_tests(problem_manager, main_solution_binary_file, executables_bin)
    problem = get_problem_by_id(problem_id)
    problem.set_names(problem_manager.names_dict)
    commit_session()
    print('Finished building package for problem {}'.format(problem_id))

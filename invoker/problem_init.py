import os

from zipfile import ZipFile
from libsbox_client import File, libsbox
from problem_manage import ProblemManager
from models import Problem
from config import Config


def extract_archive(problem_id):
    archive_path = os.path.join(Config.PROBLEMS_UPLOAD_PATH, str(problem_id) + '.zip')
    problem_path = os.path.join(Config.PROBLEMS_PATH, str(problem_id))
    if not os.path.exists(archive_path):
        return False
    ZipFile(archive_path, 'r').extractall(problem_path)
    return True


def compile_checker(problem_manager):
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
    libsbox.import_file(testlib_file)
    error_file = libsbox.create_file('error')
    compile_status, compile_task, checker_binary_file = libsbox.compile(checker_source_file,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    if compile_status != 'OK':
        print('Failed to compile checker verdict={}'.format(compile_status), flush=True)
    libsbox.export_file(checker_binary_file, problem_manager.checker_binary_path)


def prepare_and_generate_tests(problem_manager):
    main_solution_source_file = File(
        language=problem_manager.main_solution_language,
        external_path=problem_manager.main_solution_source_path
    )
    libsbox.import_file(main_solution_source_file)
    error_file = libsbox.create_file('error')
    compile_status, compile_task, main_solution_binary_file = libsbox.compile(main_solution_source_file,
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    if compile_status != 'OK':
        print('Failed to compile main solution', flush=True)
    executables_bin = []
    for executable in problem_manager.executables:
        executable_source_file = File(
            language=executable['language'],
            external_path=executable['path']
        )
        libsbox.import_file(executable_source_file)
        error_file = libsbox.create_file('error')
        compile_status, compile_task, executable_binary_file = libsbox.compile(executable_source_file,
            time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
            memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
            max_threads=10,
            stdout=error_file.internal_path,
            stderr='@_stdout'
        )
        if compile_status != 'OK':
            print('Failed to compile executable {}'.format(executable_source_file.internal_path), flush=True)
        executables_bin.append(executable_binary_file)
    for test_info in problem_manager.tests_to_generate:
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
                print('Failed to generate input for test #{} verdict={}'.format(test_number, generator_status), flush=True)
            libsbox.export_file(input_file, input_file.external_path)
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
                print('Failed to generate output for test #{} verdict={}'.format(test_number, solution_status), flush=True)
            libsbox.export_file(output_file, output_file.external_path)
        else:
            libsbox.import_file(output_file)


def init(problem_id, session): # TODO: error handler
    print('Started initializing problem {}'.format(problem_id), flush=True)
    success = extract_archive(problem_id)
    if not success:
        print('Cannot find archive for problem {}'.format(problem_id), flush=True)
        return
    problem_manager = ProblemManager(problem_id)
    compile_checker(problem_manager)
    prepare_and_generate_tests(problem_manager)
    problem = session.query(Problem).filter_by(id=problem_id).first()
    problem.set_names(problem_manager.names_dict)
    session.commit()
    print('Finished building package for problem {}'.format(problem_id), flush=True)

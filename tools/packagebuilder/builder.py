import os
import sys
import json

from zipfile import ZipFile
from kafka import KafkaConsumer

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from libsbox.client import File, Libsbox
from packagemanager import ProblemManager
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
        time_limit_ms=Config.CHECKER_COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.CHECKER_COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    if compile_status != 'OK':
        print('Failed to compile checker', flush=True)
    libsbox.export_file(checker_binary_file, problem_manager.checker_binary_path)


def prepare_and_generate_tests(problem_manager):
    main_solution_source_file = File(
        language=problem_manager.main_solution_language,
        external_path=problem_manager.main_solution_source_path
    )
    libsbox.import_file(main_solution_source_file)
    error_file = libsbox.create_file('error')
    compile_status, compile_task, main_solution_binary_file = libsbox.compile(main_solution_source_file,
        time_limit_ms=Config.SOLUTION_COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.SOLUTION_COMPILATION_MEMORY_LIMIT_KB,
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
            time_limit_ms=Config.EXECUTABLE_COMPILATION_TIME_LIMIT_MS,
            memory_limit_kb=Config.EXECUTABLE_COMPILATION_MEMORY_LIMIT_KB,
            max_threads=10,
            stdout=error_file.internal_path,
            stderr='@_stdout'
        )
        if compile_status != 'OK':
            print('Failed to compile executable', executable_source_file.internal_path, flush=True)
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
                time_limit_ms=problem_manager.time_limit_ms,
                memory_limit_kb=problem_manager.memory_limit_kb,
                stdout=input_file.internal_path,
                stderr=error_file.internal_path
            )
            if generator_status != 'OK':
                print('Failed to generate input for test #', test_number, generator_status)
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
                print('Failed to generate output for test #', test_number, solution_status)
            libsbox.export_file(output_file, output_file.external_path)
        else:
            libsbox.import_file(output_file)


def build_package(problem_id):
    print('Started building package for problem', problem_id, flush=True)
    success = extract_archive(problem_id)
    if not success:
        print('Cannot find archive for problem', problem_id, flush=True)
        return
    problem_manager = ProblemManager(problem_id)
    compile_checker(problem_manager)
    prepare_and_generate_tests(problem_manager)
    print('Finished building package for problem', problem_id, flush=True)


libsbox = Libsbox()
consumer = KafkaConsumer(
    'package',
    bootstrap_servers=[Config.KAFKA_SERVER],
    auto_offset_reset='earliest',
    session_timeout_ms=300000, # maximum time to build one package
    max_poll_records=1,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(0, 10)
)

for message in consumer:
    build_package(message.value['problem_id'])

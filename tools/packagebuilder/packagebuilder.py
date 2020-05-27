import os
import sys
import json
import asyncio

from zipfile import ZipFile
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
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
        time_limit_ms=Config.COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=error_file.internal_path,
        stderr='@_stdout'
    )
    if compile_status != 'OK':
        print('Failed to compile checker', compile_status, flush=True)
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
                time_limit_ms=Config.GENERATOR_EXECUTION_TIME_LIMIT_MS,
                memory_limit_kb=Config.GENERATOR_EXECUTION_MEMORY_LIMIT_KB,
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


def build_package(problem_id): # TODO: error handler
    print('Started building package for problem', problem_id, flush=True)
    success = extract_archive(problem_id)
    if not success:
        print('Cannot find archive for problem', problem_id, flush=True)
        return
    problem_manager = ProblemManager(problem_id)
    compile_checker(problem_manager)
    prepare_and_generate_tests(problem_manager)
    print('Finished building package for problem', problem_id, flush=True)


async def run(loop):
    nc = NATS()
    sc = STAN()

    async def message_handler(msg):
        obj = json.loads(msg.data.decode('utf-8'))
        build_package(obj['problem_id'])

    await nc.connect(servers=[Config.NATS_SERVER], loop=loop, max_reconnect_attempts=2)
    await sc.connect('test-cluster', 'packagebuilder1', nats=nc)
    await sc.subscribe('packagebuilding', queue='worker', cb=message_handler, ack_wait=300, max_inflight=1)


if __name__ == "__main__":
    libsbox = Libsbox()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()

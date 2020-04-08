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
    ZipFile(archive_path, 'r').extractall(problem_path)


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


def build_package(problem_id):
    print('Started building package for problem', problem_id, flush=True)
    extract_archive(problem_id)
    problem_manager = ProblemManager(problem_id)
    compile_checker(problem_manager)
    print('Finished building package for problem', problem_id, flush=True)


libsbox = Libsbox()
consumer = KafkaConsumer(
    'package',
    bootstrap_servers=[Config.KAFKA_SERVER],
    auto_offset_reset='earliest',
    session_timeout_ms=60000, # maximum time to build one package
    max_poll_records=1,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(0, 10)
)

for message in consumer:
    build_package(message.value['problem_id'])

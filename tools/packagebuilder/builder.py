import os
import sys
import shutil
import json

from zipfile import ZipFile
from kafka import KafkaConsumer

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from libsbox.client import Libsbox
from packagemanager import ProblemManager
from config import Config


def write_file(path, data=''):
    fout = open(path, 'w')
    fout.write(data)
    fout.close()


def clear_problem_dir():
    for item in os.listdir(Config.PROBLEM_DIR):
        os.remove(os.path.join(Config.PROBLEM_DIR, item))


def extract_archive(problem_id):
    archive_path = os.path.join(Config.PROBLEMS_UPLOAD_PATH, str(problem_id).zfill(6) + '.zip')
    problem_path = os.path.join(Config.PROBLEMS_PATH, str(problem_id).zfill(6))
    ZipFile(archive_path, 'r').extractall(problem_path)


def compile_checker(problem_manager):
    clear_problem_dir()
    checker_source_relpath = libsbox.gen_source_filename(
        Config.CHECKER_SOURCE_RELPATH, problem_manager.checker_language)
    checker_source_path = libsbox.gen_source_filename(
        Config.CHECKER_SOURCE_PATH, problem_manager.checker_language)
    shutil.copyfile(problem_manager.checker_source_path, checker_source_path)
    shutil.copyfile(problem_manager.testlib_path, Config.TESTLIB_PATH)
    write_file(Config.CHECKER_BINARY_PATH)
    write_file(Config.ERROR_PATH)
    os.chmod(Config.CHECKER_BINARY_PATH, 0o777)
    compile_object = libsbox.build_object(
        argv=libsbox.get_compile_argv(
            filename=checker_source_relpath,
            language=problem_manager.checker_language,
            output=Config.CHECKER_BINARY_RELPATH
        ),
        work_dir=Config.PROBLEM_DIR,
        time_limit_ms=Config.CHECKER_COMPILATION_TIME_LIMIT_MS,
        memory_limit_kb=Config.CHECKER_COMPILATION_MEMORY_LIMIT_KB,
        max_threads=10,
        stdout=Config.ERROR_RELPATH,
        stderr='@_stdout'
    )
    compile_response = json.loads(libsbox.send(compile_object))
    compile_status = libsbox.parse_execution_status(compile_response, compile_object)
    if compile_status != 'OK':
        print('Failed to compile checker', flush=True)
    shutil.copyfile(Config.CHECKER_BINARY_PATH, problem_manager.checker_binary_path)


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

if not os.path.exists(Config.PROBLEM_DIR):
    os.makedirs(Config.PROBLEM_DIR)

for message in consumer:
    build_package(message.value['problem_id'])

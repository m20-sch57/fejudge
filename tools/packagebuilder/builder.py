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


def extract_archive(problem_id):
    archive_path = os.path.join(Config.PROBLEMS_UPLOAD_PATH, str(problem_id).zfill(6) + '.zip')
    problem_path = ProblemManager(problem_id).package_path
    ZipFile(archive_path, 'r').extractall(problem_path)


def compile_checker(problem_manager):
    pass


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

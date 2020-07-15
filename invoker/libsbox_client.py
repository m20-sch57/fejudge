import os
import shutil
import json
import time
import socket

from config import Config


def compile_argv(source_path, binary_path, language):
    if language == 'cpp':
        return ['g++-9', source_path, '-o', binary_path, '-std=c++17', '-Wall', '-Wextra', '-O2']
    else:
        return ['cp', source_path, binary_path]


def run_argv(binary_path, language):
    if language == 'cpp':
        return ['./' + binary_path]
    elif language == 'py':
        return ['python3', binary_path]
    else:
        return ['cp', binary_path, 'output.txt']


class File:
    def __init__(self, language='txt', internal_path=None, external_path=None):
        self.language = language
        self.external_path = external_path
        self.internal_path = internal_path or os.path.basename(self.external_path)


class Libsbox:
    def __init__(self):
        socket.setdefaulttimeout(60)
        self.sock = None
        self.home_dir = Config.LIBSBOX_DIR
        if not os.path.exists(self.home_dir):
            os.makedirs(self.home_dir)
        self.clear()

    def connect(self):
        if not os.path.exists(Config.LIBSBOX_SOCKET):
            while not os.path.exists(Config.LIBSBOX_SOCKET):
                print('Waiting for libsbox to start...', end='\r')
                time.sleep(1)
            print('\nFound libsbox')
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(Config.LIBSBOX_SOCKET)

    def send(self, properties):
        self.connect()
        self.sock.send(json.dumps(properties).encode('utf-8'))
        self.sock.send(bytes([0]))
        response = self.sock.recv(1024)
        self.sock.close()
        return response.decode('utf-8')

    def clear(self, files_to_stay=[]):
        for item in os.listdir(self.home_dir):
            should_remove = True
            for file_item in files_to_stay:
                if file_item.internal_path == item:
                    should_remove = False
            if should_remove:
                os.remove(os.path.join(self.home_dir, item))

    def write_file(self, source_file: File, content):
        path = os.path.join(self.home_dir, source_file.internal_path)
        open(path, 'w').write(content)

    def create_file(self, name, language='txt', add_extension=True):
        filename = '{}.{}'.format(name, language) if add_extension else name
        path = os.path.join(self.home_dir, filename)
        open(path, 'w').write('')
        os.chmod(path, 0o777)
        return File(language=language, internal_path=filename)

    def import_file(self, source_file: File):
        path = os.path.join(self.home_dir, source_file.internal_path)
        shutil.copyfile(source_file.external_path, path)
        os.chmod(path, 0o777)

    def read_file(self, source_file: File):
        path = os.path.join(self.home_dir, source_file.internal_path)
        return open(path, 'r').read()

    def export_file(self, source_file: File, destination):
        path = os.path.join(self.home_dir, source_file.internal_path)
        shutil.copyfile(path, destination)

    def compile(self, source_file: File, **kwargs):
        binary_path = os.path.splitext(source_file.internal_path)[0]
        binary_file = self.create_file(binary_path, language=source_file.language, add_extension=False)
        argv = compile_argv(source_file.internal_path, binary_file.internal_path, source_file.language)
        properties = self.build_properties(argv=argv, work_dir=self.home_dir, **kwargs)
        response = json.loads(self.send(properties))
        status = self.parse_execution_status(response['tasks'][0], properties['tasks'][0])
        return (status, response['tasks'][0], binary_file)

    def run(self, binary_file: File, additional_argv=[], **kwargs):
        argv = run_argv(binary_file.internal_path, binary_file.language)
        argv.extend(additional_argv)
        properties = self.build_properties(argv=argv, work_dir=self.home_dir, **kwargs)
        response = json.loads(self.send(properties))
        status = self.parse_execution_status(response['tasks'][0], properties['tasks'][0])
        return (status, response['tasks'][0])

    @staticmethod
    def parse_execution_status(task_response, task_properties):
        if task_response['time_usage_ms'] >= task_properties['time_limit_ms']:
            return 'TL'
        if task_response['wall_time_usage_ms'] >= task_properties['wall_time_limit_ms']:
            return 'IL'
        if task_response['memory_limit_hit'] or task_response['oom_killed']:
            return 'ML'
        if task_response['exit_code'] != 0:
            return 'RE'
        return 'OK'

    @staticmethod
    def build_properties(**kwargs):
        return {
            "tasks": [
                {
                    "argv": kwargs['argv'],
                    "env": [],
                    "time_limit_ms": kwargs['time_limit_ms'],
                    "wall_time_limit_ms": kwargs.get('wall_time_limit_ms', 2 * kwargs['time_limit_ms']),
                    "memory_limit_kb": kwargs['memory_limit_kb'],
                    "fsize_limit_kb": kwargs.get('fsize_limit_kb', 33554432),
                    "max_files": kwargs.get('max_files', 128),
                    "max_threads": kwargs.get('max_threads', 1),
                    "stdin": kwargs.get('stdin', None),
                    "stdout": kwargs.get('stdout', None),
                    "stderr": kwargs.get('stderr', None),
                    "need_ipc": False,
                    "use_standard_binds": True,
                    "binds": [
                        {
                            "inside": ".",
                            "outside": kwargs['work_dir'],
                            "flags": 1
                        }
                    ]
                }
            ]
        }


libsbox = Libsbox()

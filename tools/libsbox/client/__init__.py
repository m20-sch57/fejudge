import os
import socket
import json
import time

from libsbox.client.config import Config


class Libsbox:
    def __init__(self):
        self.sock = None
        socket.setdefaulttimeout(60)

    def connect(self):
        if not os.path.exists(Config.SOCKET_FILE):
            while not os.path.exists(Config.SOCKET_FILE):
                print('Waiting for libsbox to start...', end='\r', flush=True)
                time.sleep(1)
            print()
            print('Found libsbox', flush=True)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(Config.SOCKET_FILE)

    def send(self, obj):
        self.connect()
        self.sock.send(json.dumps(obj).encode('utf-8'))
        self.sock.send(bytes([0]))
        response = self.sock.recv(1024)
        self.sock.close()
        return response.decode('utf-8')

    @staticmethod
    def build_object(**kwargs):
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

    @staticmethod
    def gen_source_filename(filename, language):
        return '{}.{}'.format(filename, language)

    @staticmethod
    def get_compile_argv(filename, language, output):
        if language == 'cpp':
            return ['g++-9', filename, '-o', output, '-std=c++17', '-Wall', '-Wextra', '-O2']
        else:
            return ['cp', filename, output]

    @staticmethod
    def get_run_argv(filename, language, additional_argv=[]):
        argv = []
        if language == 'cpp':
            argv = ['./' + filename]
        elif language == 'py':
            argv = ['python3', filename]
        else:
            argv = ['cp', filename, 'output.txt']
        argv.extend(additional_argv)
        return argv

    @staticmethod
    def parse_execution_status(response, obj):
        task_response = response['tasks'][0]
        task_obj = obj['tasks'][0]
        if task_response['time_usage_ms'] >= task_obj['time_limit_ms']:
            return 'TL'
        if task_response['wall_time_usage_ms'] >= task_obj['wall_time_limit_ms']:
            return 'IL'
        if task_response['memory_limit_hit'] or task_response['oom_killed']:
            return 'ML'
        if task_response['exit_code'] != 0:
            return 'RE'
        return 'OK'

    @staticmethod
    def parse_checker_status(checker_response):
        exit_code = checker_response['tasks'][0]['exit_code']
        if exit_code == 0:
            return 'OK'
        if exit_code == 1:
            return 'WA'
        if exit_code == 2:
            return 'PE'
        return 'FAIL'

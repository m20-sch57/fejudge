import os
import socket
import json
import time

from config import Config


class Libsbox:
    @staticmethod
    def connect():
        while not os.path.exists(Config.SOCKET_FILE):
            print('Waiting for libsbox to start...')
            time.sleep(1)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(Config.SOCKET_FILE)
        return client

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
    def send(obj):
        client = Libsbox.connect()
        client.send(json.dumps(obj).encode('utf-8'))
        client.send(bytes([0]))
        response = client.recv(1024)
        client.close()
        return response.decode('utf-8')

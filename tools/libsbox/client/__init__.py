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


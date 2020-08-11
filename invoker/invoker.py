import json
import time
import socket
import socketio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pynats import NATSClient
from pynats.exceptions import NATSError
from socketio.exceptions import ConnectionError
from libsbox_client import Libsbox
from models import Base
from config import Config


def message_handler(msg):
    from evaluate import evaluate, EvaluationError
    from problem_init import init, InitializationError

    obj = json.loads(msg.payload.decode('utf-8'))
    if obj.get('type') == 'evaluate':
        try:
            evaluate(obj.get('submission_id'))
        except EvaluationError as e:
            print(e.cause)
            print(e.details)
    elif obj.get('type') == 'problem_init':
        try:
            init(obj.get('problem_id'))
        except InitializationError as e:
            print(e.cause)
            print(e.details)
    else:
        print('Unsupported type of query: {}'.format(obj.get('type')))


def connect_to_socketio():
    while True:
        try:
            sio.connect(Config.SOCKETIO_URL)
            print('Connecting to socketio - success')
            return
        except ConnectionError:
            print('Connecting to socketio...', end='\r')
            time.sleep(1)


def connect_to_nats():
    while True:
        try:
            nats.connect()
            nats.subscribe('invokers', queue='worker', callback=message_handler)
            print('Connecting to NATS - success')
            nats.wait()
        except (socket.error, NATSError):
            print('Connecting to NATS...', end='\r')
            time.sleep(1)


def run():
    try:
        connect_to_socketio()
        connect_to_nats()
    except KeyboardInterrupt:
        exit()


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
session = Session(bind=engine)

sio = socketio.Client()
nats = NATSClient(Config.NATS_URL, name=Config.INVOKER_NAME)
libsbox = Libsbox()

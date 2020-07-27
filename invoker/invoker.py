import json
import time
import socket
import socketio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pynats import NATSClient
from pynats.exceptions import NATSError
from socketio.exceptions import ConnectionError
from evaluate import evaluate
from problem_init import init, InitializationError
from models import Base
from config import Config


def message_handler(msg):
    obj = json.loads(msg.payload.decode('utf-8'))
    if obj['type'] == 'evaluate':
        evaluate(obj['submission_id'], session, sio)
    elif obj['type'] == 'problem_init':
        try:
            init(obj['problem_id'], session)
        except InitializationError as e:
            print(e.cause)
            print(e.details)
    else:
        print('Unsupported type of query: {}'.format(obj['type']))


def connect_to_socketio():
    while True:
        try:
            sio.connect(Config.SOCKETIO_SERVER)
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


if __name__ == "__main__":
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    session = Session(bind=engine)

    sio = socketio.Client()
    nats = NATSClient(Config.NATS_SERVER, name=Config.INVOKER_NAME)

    try:
        connect_to_socketio()
        connect_to_nats()
    except KeyboardInterrupt:
        exit()

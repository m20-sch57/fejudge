import os
import logging

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData
from pynats import NATSClient
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, logger=app.logger)

file_handler = logging.FileHandler(app.config['LOG_FILE'])
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
app.logger.addHandler(file_handler)

db = SQLAlchemy(app, metadata=MetaData(naming_convention=Config.NAMING_CONVENTION))
migrate = Migrate(app, db, render_as_batch=True, compare_type=True)

nats = NATSClient(Config.NATS_SERVER, name='producer1')

login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'info auto-dismiss'


from app import routes, events, models

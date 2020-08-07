from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from pynats import NATSClient
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

nats = NATSClient(Config.NATS_URL, name='app')

login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'info auto-dismiss'


from app import routes, events, models

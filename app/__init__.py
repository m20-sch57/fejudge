from flask import Flask
from flask_socketio import SocketIO
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from pynats import NATSClient
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
db = SQLAlchemy(app, metadata=MetaData(naming_convention=Config.NAMING_CONVENTION))
migrate = Migrate(app, db, render_as_batch=True, compare_type=True)
nats = NATSClient(Config.NATS_SERVER, name='producer1')

login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'info auto-dismiss'


from app import routes, events, models

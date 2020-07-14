import json

from flask import Flask
from flask_socketio import SocketIO
from flask_avatars import Avatars
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from pynats import NATSClient
from config import Config


def submit_to_queue(group, obj):
    nats.connect()
    nats.publish(group, payload=json.dumps(obj).encode('utf-8'))
    nats.close()


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
db = SQLAlchemy(app, metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app, db, render_as_batch=True, compare_type=True)
nats = NATSClient(Config.NATS_SERVER, name='producer1')
mail = Mail(app)

avatars = Avatars(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'info auto-dismiss'


from app import routes, events, models

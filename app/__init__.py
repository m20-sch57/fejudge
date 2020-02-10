import json

from flask import Flask
from flask_avatars import Avatars
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import MetaData
from kafka import KafkaProducer
from config import Config


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app, db, render_as_batch=True, compare_type=True)
mail = Mail(app)
producer = KafkaProducer(
    bootstrap_servers=[app.config['KAFKA_SERVER']],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    api_version=(0, 10)
)

avatars = Avatars(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'alert-info'


from app import routes, models

import json
import asyncio

from flask import Flask
from flask_avatars import Avatars
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from nats.aio.client import Client as NATS, NatsError
from stan.aio.client import Client as STAN
from config import Config


async def connect_to_nats():
    await nc.connect(servers=[Config.NATS_SERVER], loop=loop, max_reconnect_attempts=2)
    await sc.connect('test-cluster', 'producer1', nats=nc)


async def submit_to_nats(group, obj):
    await sc.publish(group, json.dumps(obj).encode('utf-8'))


def submit_data(group, obj):
    loop.run_until_complete(submit_to_nats(group, obj))


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

nc = NATS()
sc = STAN()
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(connect_to_nats())
except NatsError as e:
    print(e)

avatars = Avatars(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'alert-info'


from app import routes, models

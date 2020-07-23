import os
import shutil

from datetime import timedelta

from config import Config
from app import db
from app.services import register_user, create_contest


def init_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)
        return
    for item in os.listdir(folder):
        path = os.path.join(folder, item)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def clear_database(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


clear_database(db.session)
init_folder(Config.SUBMISSIONS_DOWNLOAD_PATH)
init_folder(Config.PROBLEMS_UPLOAD_PATH)
init_folder(Config.PROBLEMS_PATH)

user = register_user(
    username='Kuyanov',
    email='feodor.kuyanov@gmail.com',
    password='fedor2002'
)
create_contest(
    name='Идейные задачи',
    duration=timedelta(hours=24),
    owner=user
)

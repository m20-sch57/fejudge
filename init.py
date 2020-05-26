import os
import shutil

from config import Config
from app import db
from app.models import User, Contest, Problem, Submission, ContestRequest
from datetime import timedelta


def clear_folder(folder):
    if not os.path.isdir(folder):
        print('Clear folder {}: folder not exist, creating...'.format(folder))
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
clear_folder(Config.SUBMISSIONS_LOG_PATH)
clear_folder(Config.SUBMISSIONS_DOWNLOAD_PATH)
clear_folder(Config.PROBLEMS_UPLOAD_PATH)
clear_folder(Config.PROBLEMS_PATH)

u = User(
    username='Kuyanov',
    first_name='Fedor',
    last_name='Kuyanov',
    email='feodor.kuyanov@gmail.com'
)
u.set_password('fedor2002')
db.session.add(u)

c = Contest(name='Идейные задачи', duration=timedelta(hours=24), owner=u)
db.session.add(c)
db.session.commit()

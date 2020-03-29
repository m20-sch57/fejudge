import os
import shutil

from config import Config
from app import db
from app.models import User, Contest, Problem, Submission, ContestRequest
from datetime import timedelta


def clear_folder(folder):
    if not os.path.isdir(folder):
        print('Clear folder {}: folder not exist.'.format(folder))
        return
    for item in os.listdir(folder):
        path = os.path.join(folder, item)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()
    clear_folder(Config.SUBMISSIONS_LOG_PATH)
    clear_folder(Config.SUBMISSIONS_DOWNLOAD_PATH)
    clear_folder(Config.PROBLEMS_UPLOAD_PATH)
    clear_folder(Config.PROBLEMS_PATH)


clear_data(db.session)

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
# problems = []
# for i in range(4):
#     p = Problem(
#         contest=c,
#         number=i+1,
#         problem_type='Programming',
#         max_score=100
#     )
#     db.session.add(p)
#     problems.append(p)


db.session.commit()

# for i in range(10):
#     e = Contest(name='Тренировка №{} по теме средних веков'.format(i + 1), duration=timedelta(minutes=1))
#     db.session.add(e)
#     for j in range(10):
#         q = Problem(contest=e, number=j+1, problem_type='Test',
#             statement='Это текст вопроса {}, напишите сюда его условие. Нам же было очень лень...'.format(j + 1))
#         db.session.add(q)
# db.session.commit()

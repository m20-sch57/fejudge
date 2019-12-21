import os
import shutil

from config import basedir
from app import db
from app.models import User, Contest, Problem, Submission
from datetime import timedelta

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()

def clear_submissions():
    shutil.rmtree(os.path.join(basedir, 'submissions'))
    os.makedirs(os.path.join(basedir, 'submissions'))
    os.chmod(os.path.join(basedir, 'submissions'), 0o777)
    shutil.rmtree(os.path.join(basedir, 'logs', 'submissions'))
    os.makedirs(os.path.join(basedir, 'logs', 'submissions'))
    os.chmod(os.path.join(basedir, 'logs', 'submissions'), 0o777)


clear_data(db.session)
clear_submissions()

u = User(
    username='Kuyanov',
    fullname='Fedor Kuyanov',
    email='feodor.kuyanov@gmail.com',
    phone='8 (800) 555-35-35',
)
u.set_password('fedor2002')
db.session.add(u)

c = Contest(name='Идейные задачи', duration=timedelta(hours=24))
db.session.add(c)
problems = []
for i in range(4):
    p = Problem(
        contest=c,
        number=i+1,
        name='A+B',
        problem_type='Programming',
        statement='Это условие задачи.\nВы должны догадаться сами и сдать решение',
        max_score=100
    )
    db.session.add(p)
    problems.append(p)


db.session.commit()

# for i in range(10):
#     e = Contest(name='Тренировка №{} по теме средних веков'.format(i + 1), duration=timedelta(minutes=1))
#     db.session.add(e)
#     for j in range(10):
#         q = Problem(contest=e, number=j+1, problem_type='Test',
#             statement='Это текст вопроса {}, напишите сюда его условие. Нам же было очень лень...'.format(j + 1))
#         db.session.add(q)
# db.session.commit()

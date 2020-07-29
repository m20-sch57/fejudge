from datetime import timedelta
from app.services import register_user, create_contest


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

from datetime import timedelta
from app import db
from app.services import register_user, create_contest


for table in reversed(db.metadata.sorted_tables):
    db.session.execute(table.delete())
db.session.commit()

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

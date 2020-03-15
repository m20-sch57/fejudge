from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa


Base = declarative_base()


class Submission(Base):
    __tablename__ = 'submission'
    id = sa.Column(sa.Integer, primary_key=True)
    status = sa.Column(sa.String(32))
    score = sa.Column(sa.Integer)
    details = sa.Column(sa.Text, default='{}')

    def __repr__(self):
        return '<SUBMISSION ID={} STATUS={} SCORE={}>'.format(self.id, self.status, self.score)

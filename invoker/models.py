from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import json


Base = declarative_base()


class Problem(Base):
    __tablename__ = 'problem'
    id = sa.Column(sa.Integer, primary_key=True)
    names = sa.Column(sa.Text, default='{}')
    max_submissions = sa.Column(sa.Integer, default=50)

    submissions = sa.orm.relationship('Submission', backref='problem', lazy='dynamic')

    def __repr__(self):
        return '<PROBLEM {}>'.format(self.id)

    def set_names(self, names_dict):
        self.names = json.dumps(names_dict)


class Submission(Base):
    __tablename__ = 'submission'
    id = sa.Column(sa.Integer, primary_key=True)
    problem_id = sa.Column(sa.Integer, sa.ForeignKey('problem.id'))
    language = sa.Column(sa.String(32))
    source = sa.Column(sa.Text)
    status = sa.Column(sa.String(32))
    score = sa.Column(sa.Integer)
    protocol = sa.Column(sa.Text, default='{}')

    def __repr__(self):
        return '<SUBMISSION ID={} STATUS={} SCORE={}>'.format(self.id, self.status, self.score)

    def set_protocol(self, protocol):
        self.protocol = json.dumps(protocol)

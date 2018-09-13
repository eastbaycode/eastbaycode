from datetime import datetime
from flask_login import UserMixin
from app import db
from app import login

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    # lastname = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)
    active = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    problems = db.relationship("Problems", backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<Users {0} {1} {2} {3}>'.format(self.id, self.name,
                self.email, self.registered_date)

class Problems(db.Model):
    __tablename__ = "problems"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(120))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    version = db.Column(db.Integer)
    question = db.Column(db.Text())
    solution = db.Column(db.Text())
    testcases = db.relationship("TestCases", backref='problem', lazy='dynamic')

    def __repr__(self):
        return "<Problems {}".format(self.question)

class Examples(db.Model):
    __tablename__ = "examples"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    input = db.Column(db.Text())
    output = db.Column(db.Text())
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'))
    # relationship with problem table
    def __repr__(self):
        return "<Examples {0} {1}".format(self.input, self.output)

class TestCases(db.Model):
    __tablename__ = "testcases"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'))
    input = db.Column(db.Text())
    output = db.Column(db.Text())
    flags = db.Column(db.Text())

    def __repr__(self):
        return "<TestCases {0} {1} {2}".format(self.problem_id,
                self.input, self.output)

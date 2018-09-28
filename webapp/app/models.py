from datetime import datetime
from flask_login import UserMixin
from app import db
from app import login
import redis
import rq

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

# association table for Users and Courses (many-to-many relationship)
registrations = db.Table('registrations',
                        db.Column('student_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
                        )

# association table for Assignments and Problems (many-to-many relationship)
assignments_problems = db.Table('assignments_problems',
                            db.Column('assignment_id', db.Integer, db.ForeignKey('assignments.id')),
                            db.Column('problem_id', db.Integer, db.ForeignKey('problems.id'))
                            )

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
    problems = db.relationship("Problems", cascade="all,delete", backref='creator', lazy='dynamic')
    courses = db.relationship("Courses", cascade="all,delete", secondary=registrations,
                              backref=db.backref('student', lazy='dynamic'),
                              lazy='dynamic')
    professor = db.relationship("Courses", cascade="all,delete", backref='professor', lazy='dynamic')
    tasks = db.relationship("Task", backref='user', lazy='dynamic')

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
    examples = db.relationship("Examples", cascade="all,delete", backref='problem', lazy='dynamic')
    testcases = db.relationship("TestCases", cascade="all,delete", backref='problem', lazy='dynamic')

    def __repr__(self):
        return "<Problems {}>".format(self.question)

class Examples(db.Model):
    __tablename__ = "examples"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    input = db.Column(db.Text())
    output = db.Column(db.Text())
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'))
    # relationship with problem table
    def __repr__(self):
        return "<Examples {0} {1}>".format(self.input, self.output)

class TestCases(db.Model):
    __tablename__ = "testcases"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'))
    input = db.Column(db.Text())
    output = db.Column(db.Text())
    flags = db.Column(db.Text())

    def __repr__(self):
        return "<TestCases {0} {1} {2}>".format(self.problem_id,
                self.input, self.output)

class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    startdate = db.Column(db.Date)
    enddate = db.Column(db.Date)
    semester = db.Column(db.String(120))
    assignments = db.relationship("Assignments", cascade="all,delete", backref='course', lazy='dynamic')

    def professor(self):
        professor = Users.query.filter(self.professor_id==Users.id).first()
        return professor.name

    def __repr__(self):
        return "<Courses {0} {1} {2}>".format(self.title, self.professor_id,
                                            self.semester)

class Assignments(db.Model):
    __tablename__  = 'assignments'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    startdate = db.Column(db.Date)
    enddate = db.Column(db.Date)
    grade = db.Column(db.Integer)
    problems = db.relationship("Problems", secondary=assignments_problems,
                                backref=db.backref('assignment', lazy='dynamic'),
                                lazy='dynamic'
                                )

    def __repr__(self):
        return "<Assignments {0} {1}>".format(course_id, problems)


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user_id'))
    complete = db.Column(db.Boolean, default='False')

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptoins.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def is_complete(self):
        job = self.get_rq_job()
        return job.meta.get('complete')

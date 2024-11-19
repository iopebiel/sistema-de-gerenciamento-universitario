from . import db
from sqlalchemy.sql import func

class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    studentnumber = db.Column(db.String(7), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    course = db.Column(db.String(3), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    classgroup = db.Column(db.String(4), nullable=False)
    unit = db.Column(db.String(2), nullable=False)
    
class Subject(db.Model):
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    teacher = db.Column(db.String(60), nullable=False)
    course = db.Column(db.String(3), nullable=False)
    day = db.Column(db.String(50), nullable=False)
    schedule = db.Column(db.Time, nullable=False)
    classesperday = db.Column(db.Integer, nullable=False)
    totalclasses = db.Column(db.Integer, nullable=False)

class StudentSubject(db.Model):
    __tablename__ = 'student_subject'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    studentid = db.Column(db.Integer, db.ForeignKey('student.id'))
    subjectid = db.Column(db.Integer, db.ForeignKey('subject.id'))
    enrollmentdate = db.Column(db.DateTime, nullable=False, server_default=func.now())
    grade = db.Column(db.Float, nullable=True)
    active = db.Column(db.Boolean, nullable=False)

class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    studentsubjectid = db.Column(db.Integer, db.ForeignKey('student_subject.id'))
    insertiondate = db.Column(db.DateTime, nullable=False, server_default=func.now())
    deadline = db.Column(db.DateTime)
    grade = db.Column(db.Float)
    description = db.Column(db.String(500))
    complete = db.Column(db.Boolean, nullable=False)
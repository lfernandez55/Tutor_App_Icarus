# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from app import db

class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class TutorLanguages(db.Model):
    __tablename__ = 'tutors_languages'
    id = db.Column(db.Integer(), primary_key=True)
    language_id = db.Column(db.Integer(), db.ForeignKey('languages.id', ondelete='CASCADE'))
    tutor_id = db.Column(db.Integer(), db.ForeignKey('tutor.id', ondelete='CASCADE'))


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class TutorCourses(db.Model):
    __tablename__ = 'tutors_courses'
    id = db.Column(db.Integer(), primary_key=True)
    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id', ondelete='CASCADE'))
    tutor_id = db.Column(db.Integer(), db.ForeignKey('tutor.id', ondelete='CASCADE'))

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))

    # see https://stackoverflow.com/questions/7671886/attributeerror-instrumentedlist-object-has-no-attribute
    tutor = db.relationship("Tutor", backref='users', uselist=False, cascade='all')
    

# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class Tutor(db.Model):
    __tablename__ = 'tutor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    tutor_phone = db.Column(db.String(50)) 
    display_in_sched = db.Column(db.Boolean, unique=False)
    dates = db.relationship("Time", backref='tutor', cascade='all')

    languages = db.relationship('Language', secondary='tutors_languages',
                    backref=db.backref('users', lazy='dynamic'))   

    courses = db.relationship('Course', secondary='tutors_courses',
                backref=db.backref('users', lazy='dynamic')) 

class Time(db.Model):
    __tablename__ = 'time'
    id = db.Column(db.Integer(), primary_key=True)
    time_day = db.Column(db.Integer())
    time_start = db.Column(db.Time())
    time_end = db.Column(db.Time())
    # tutor = db.relationship('Tutor', uselist=False)
    tutor_id = db.Column(db.Integer(), db.ForeignKey('tutor.id', ondelete='CASCADE'))
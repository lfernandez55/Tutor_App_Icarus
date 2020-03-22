from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, SelectField, validators, PasswordField, FieldList, FormField, IntegerField

class TimeCustomForm(FlaskForm):
    timeDay = IntegerField(label="Day of Week")
    timeStart = StringField(label='Time Start')
    timeEnd = StringField(label='Time End')
    class Meta:
        # No need for csrf token in this child form
        csrf = False


class UserCustomForm(FlaskForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    email = StringField('Email', validators=[
        validators.DataRequired('Email is required')])
    password = PasswordField('Password')
    roles = SelectMultipleField(label='Roles', coerce=int)

    # tutor = FormField(TutorCustomForm, 'Tutor Specific Fields')
    # add_child = SubmitField(label='Tutor Specific Info')

    submit = SubmitField('Save')

class RoleCustomForm(FlaskForm):
    name = StringField('Role name', validators=[
        validators.DataRequired('Role name is required')])
    # label = StringField('Role label')
    submit = SubmitField('Save')

    class Meta:
        # No need for csrf token in this child form
        csrf = False

class TutorCustomForm(UserCustomForm):
    phone = StringField(label='Phone')
    dates = FieldList(FormField(TimeCustomForm), label='dates')
    add_child = SubmitField(label='Add Date')

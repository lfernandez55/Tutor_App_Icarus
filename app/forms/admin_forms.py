from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, \
                    SelectField, validators, PasswordField, FieldList, FormField, \
                    IntegerField, HiddenField, BooleanField, ValidationError
from wtforms_components import TimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, widgets
from app.models.user_models import Language
from app.models.user_models import User

class TimeCustomForm(FlaskForm):
    id = HiddenField(label="")
    time_day = SelectField(label="Day of Week",choices=[(1,'Monday'),(2,'Tuesday'),(3,'Wednesday'),(4,'Thursday'),(5,'Friday')], coerce=int)
    time_start = TimeField(label='Time Start') #see: https://stackoverflow.com/questions/44020690/wtforms-equivalent-to-input-type-time
    time_end = TimeField(label='Time End')
    
    class Meta:
        # No need for csrf token in this child form
        csrf = False


class UserCustomForm(FlaskForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    email = StringField('Email')
    password = PasswordField('Password', validators=[
        validators.DataRequired('First name is required')])
    roles = SelectMultipleField(label='Roles', coerce=int)

    # tutor = FormField(TutorCustomForm, 'Tutor Specific Fields')
    # add_child = SubmitField(label='Tutor Specific Info')

    submit = SubmitField('Save')

    def validate_email(form, field):
        print("DDDDDDDDDDDDDDDDDDDDDDDD:", form, field)
        if field.raw_data == "":
            raise ValidationError('Email cannot be blank')
        else:
            result = User.query.filter_by(email=field.data).first()
            if result:
                raise ValidationError('Email must be unique')
            
        # if not field.raw_data:
        #     result = User.query.filter_by(email=form.field.data).first()
        #     if result:
        #         raise ValidationError('Email must be unique')
        # raise ValidationError('Email cannot be blank')

class RoleCustomForm(FlaskForm):
    name = StringField('Role name', validators=[
        validators.DataRequired('Role name is required')])
    # label = StringField('Role label')
    submit = SubmitField('Save')

    # class Meta:
    #     # No need for csrf token in this child form
    #     csrf = False

# class TutorCustomForm(UserCustomForm):
#     phone = StringField(label='PhonexS')
#     display_in_sched = BooleanField(label='Display in Schedule')
#     # for the below attribute see: https://stackoverflow.com/questions/48845098/how-to-make-a-list-of-booleanfield-using-wtforms
#     languages = QuerySelectMultipleField(
#         query_factory=lambda: Language.query.all(),
#         get_label='name',
#         widget=widgets.ListWidget(prefix_label=False),
#         option_widget=widgets.CheckboxInput()
#     )
#     # ideally the next field should be remove_time_id = HiddenField(label="") 
#     # however in the template, the line {{ form.hidden_tag() }} renders this field multiple times
#     # it looks like a bug in wtforms that happens when child forms are used. we resolve it by hiding the field using javascript in the form
#     remove_time_id = StringField(label="")
#     dates = FieldList(FormField(TimeCustomForm), label='dates')
#     add_time = SubmitField(label='Add Date')
#     remove_time = SubmitField(label='Remove Date')
    

# the multicheckbox example comes from https://gist.github.com/doobeh/4668212
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    # for next line see: https://stackoverflow.com/questions/39395125/wtforms-selectmultiplefield-disable-validation
    def pre_validate(self, form):
        """per_validation is disabled"""

class TutorCustomForm(UserCustomForm):
    phone = StringField(label='Phone')
    display_in_sched = BooleanField(label='Display in Schedule')
    # for the below attribute see: from https://gist.github.com/doobeh/4668212
    languages = MultiCheckboxField('Label')
    courses = MultiCheckboxField('Label')
    # ideally the next field should be remove_time_id = HiddenField(label="") 
    # however in the template, the line {{ form.hidden_tag() }} renders this field multiple times
    # it looks like a bug in wtforms that happens when child forms are used. we resolve it by hiding the field using javascript in the form
    remove_time_id = StringField(label="")
    dates = FieldList(FormField(TimeCustomForm), label='dates')
    add_time = SubmitField(label='Add Date')
    remove_time = SubmitField(label='Remove Date')
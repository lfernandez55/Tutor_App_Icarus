from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for, current_app
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import User, Role, Tutor, Time, Course, Language
from app.forms.admin_forms import UserCustomForm, RoleCustomForm, TutorCustomForm

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

@admin_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('admin/admin_page.html')

@admin_blueprint.route('/admin/list_users', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_list_users():
    if request.method == 'GET':
        # users = User.query.all()
        users = User.query.order_by(User.email.asc())
    else:
        search_term = request.form["search_term"]
        search_term = "%{}%".format(search_term)
        users = User.query.filter(User.email.like(search_term)).all()
    
    return render_template('admin/admin_list_users.html', users=users)  

#############################BEGIN CREATE EDIT DELETE TUTOR VIEWS######################################
#######################################################################################################

@admin_blueprint.route('/admin/create_tutor', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_create_tutor():

    form = TutorCustomForm()
    # this next line needed for a validation in the user model class
    form.id=-1

    # adding the full set of select options to the select list 
    addTutorFormChoices(form)
    if form.add_time.data:
        form.dates.append_entry()
        return render_template('admin/admin_create_edit_tutor.html', form=form, time_state='manage_time', state='Create')

    if form.remove_time.data:
        removeTime(form)
        return render_template('admin/admin_create_edit_tutor.html', form=form, time_state='manage_time', state='Create')

    if form.validate_on_submit():
        user = User()
        user.first_name  = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.roles = []
        for role_id in form.roles.data:
            roleObj = Role.query.filter(Role.id == role_id).first()
            user.roles.append(roleObj)

        user.languages = []
        for lang in form.languages:
            if lang.checked is True:
                langObj = Language.query.filter(Language.id == lang.data).first()
                user.languages.append(langObj)

        user.courses = []
        for course in form.courses:
            if course.checked is True:
                courseObj = Course.query.filter(Course.id == course.data).first()
                user.courses.append(courseObj)

        user.password=current_app.user_manager.password_manager.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        tutor = Tutor()
        tutor.tutor_phone = form.phone.data
        tutor.display_in_sched = form.display_in_sched.data
        tutor.user_id = user.id
        db.session.add(tutor)
        db.session.commit()

        for date_group in form.dates:
            time = Time()
            time.time_day = date_group['time_day'].data
            time.time_start = date_group['time_start'].data
            time.time_end = date_group['time_end'].data
            time.tutor_id = tutor.id
            db.session.add(time)
            db.session.commit()

        flash('User Created!!', 'success')
        return redirect(url_for('admin.admin_list_users'))
    return render_template('admin/admin_create_edit_tutor.html', form=form, state='Create')

@admin_blueprint.route('/admin/edit_tutor/<user_id>', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_edit_tutor(user_id):
    user = User.query.filter(User.id == user_id).first()

    # determining the options that the user has selected/checked
    current_roles = []
    for role in user.roles:
        current_roles.append(str(role.id))

    current_languages = []
    for lang in user.languages:
        current_languages.append(lang.id)

    current_courses = []
    for course in user.courses:
        current_courses.append(course.id)

    if user.tutor is None:
        form = TutorCustomForm(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email, 
        roles=current_roles, languages=current_languages, courses=current_courses)
    else:
        form = TutorCustomForm(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email, 
        roles=current_roles, languages=current_languages, courses=current_courses, phone=user.tutor.tutor_phone, display_in_sched=user.tutor.display_in_sched, dates=user.tutor.dates)

    # this next line needed for a validation in the model user, see user_models.py.  i don't know why it's not 
    # instantiated above
    form.id = user.id 

    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    # the above is a subset of the below
    # the above is the checked boxes, the below is all the check boxes
    # the above is the selected items, the below is all the items that can be selected
    addTutorFormChoices(form)
    


    if form.add_time.data:
        form.dates.append_entry()
        return render_template('admin/admin_create_edit_tutor.html', form=form, time_state='manage_time', state='Edit')

    if form.remove_time.data:
        removeTime(form)
        return render_template('admin/admin_create_edit_tutor.html', form=form, time_state='manage_time', state='Edit')

    if form.validate_on_submit():
        user.first_name  = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.roles = []
        for role_id in form.roles.data:
            roleObj = Role.query.filter(Role.id == role_id).first()
            user.roles.append(roleObj)

        user.languages = []
        for lang in form.languages:
            if lang.checked is True:
                langObj = Language.query.filter(Language.id == lang.data).first()
                user.languages.append(langObj)

        user.courses = []
        for course in form.courses:
            if course.checked is True:
                courseObj = Course.query.filter(Course.id == course.data).first()
                user.courses.append(courseObj)

        if form.password.data != "not_updated_flag":
            user.password=current_app.user_manager.password_manager.hash_password(form.password.data)

        # kludge:  to accomodate the original admin and manager accounts that hadn't been assigned any tutor attributes
        # these need to be added regardless of whether the user has the tutor role. . . 
        # A better approach to implement down the road is to see if any tutor specific attributes have been filled out in the form.
        # If they have then run these next couple of lines.  Otherwise dont. 
        if user.tutor is None:
            tutor = Tutor()
            tutor.user_id = user.id
            db.session.add(tutor)
            db.session.commit()


        user.tutor.tutor_phone = form.phone.data
        user.tutor.display_in_sched = form.display_in_sched.data
        
        for date_group in form.dates:
            if date_group['id'].data != "":
               time = Time.query.filter(Time.id == date_group['id'].data).first()
            else:
               time = Time()
            time.time_day = date_group['time_day'].data
            time.time_start = date_group['time_start'].data
            time.time_end = date_group['time_end'].data
            user.tutor.dates.append(time)
        db.session.add(user)
        db.session.commit()

        flash('User Updated!!', 'success')
        return redirect(url_for('admin.admin_list_users'))
    print("form.password:", form.first_name)
    return render_template('admin/admin_create_edit_tutor.html', form=form, state='Edit')


@admin_blueprint.route('/admin/delete_user/<user_id>')
@roles_required('admin')  
def admin_delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash('User Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_users'))

def addTutorFormChoices(form):
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices

    langCollection = Language.query.all()
    lang_list = []
    for lang in langCollection:
        lang_list.append(lang.name)
    lang_choices = list(enumerate(lang_list,start=1))
    form.languages.choices = lang_choices

    courseCollection = Course.query.all()
    course_list = []
    for course in courseCollection:
        course_list.append(course.name)
    course_choices = list(enumerate(course_list,start=1))
    form.courses.choices = course_choices

def removeTime(form):
        # since we are popping off items from the end of the list rather than the beginning the index of the item to remove is:
        index_of_item_to_remove = len(form.dates) - int(form.remove_time_id.data)

        # pop off all the items in the fieldlist, and append them to the reverselist with the exception of the item to remove
        reversed_list = []
        number_of_dates = len(form.dates)
        for x in range(number_of_dates ):
            if index_of_item_to_remove == x:
                popped_entry = form.dates.pop_entry()
            else:
                reversed_list.append(form.dates.pop_entry())

        # reverse the reversedlist and repopulate form.dates
        form.dates = list(reversed(reversed_list))
        if popped_entry.data['id']:
                child = Time.query.filter(Time.id == popped_entry.data['id']).first()
                db.session.delete(child)
                db.session.commit()

#############################END CREATE EDIT DELETE TUTOR VIEWS######################################
#######################################################################################################


@admin_blueprint.route('/admin/list_roles', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_list_roles():
    roles = Role.query.order_by(Role.name.asc())
    for role in roles:
        print(role.name)
    return render_template('admin/admin_list_roles.html', roles=roles) 

@admin_blueprint.route('/admin/create_role', methods=['GET', 'POST'])
@roles_required('admin')  
def admin_create_role():
    form = RoleCustomForm()

    if form.validate_on_submit():
        role = Role()
        role.name  = form.name.data
        db.session.add(role)
        db.session.commit()
        flash('Role Created!!', 'success')
        return redirect(url_for('admin.admin_list_roles'))
    return render_template('admin/admin_create_edit_role.html', form=form, state='Create')

@admin_blueprint.route('/admin/edit_role/<role_id>', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_edit_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()

    form = RoleCustomForm(id=role.id, name=role.name)

    if form.validate_on_submit():
        role.name  = form.name.data
        db.session.add(role)
        db.session.commit()
        flash('Role Updated!!', 'success')
        return redirect(url_for('admin.admin_list_roles'))
    return render_template('admin/admin_create_edit_role.html', form=form, state='Edit')

@admin_blueprint.route('/admin/delete_role/<role_id>')
@roles_required('admin')  
def admin_delete_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    db.session.delete(role)
    db.session.commit()
    flash('Role Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_roles'))




####################################################################################
#############################Course Views###########################################

@admin_blueprint.route('/admin/list_courses', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_list_courses():
    courses = Course.query.order_by(Course.name.asc())
    for course in courses:
        print(course.name)
    return render_template('admin/admin_list_courses.html', courses=courses) 




@admin_blueprint.route('/admin/create_course', methods=['GET', 'POST'])
@roles_required('admin')  
def admin_create_course():
    error_msg = ""
    course = Course()

    if request.method == 'POST':
        # email validation
        other_course = Course.query.filter(Course.name == request.form['name'] ).first()
        if (other_course is not None) and (other_course.id != course.id):
            error_msg = "This course name is already being used"
            flash('This course name is already being used!!', 'error')
        else:
            course.name  = request.form['name']
            db.session.add(course)
            db.session.commit()
            flash('Course Created!!', 'success')
            return redirect(url_for('admin.admin_list_courses'))
    return render_template('admin/admin_create_edit_course.html', course=course, error_msg=error_msg, verb="Create")



@admin_blueprint.route('/admin/edit_course/<course_id>', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_edit_course(course_id):
    error_msg=""
    course = Course.query.filter(Course.id == course_id).first()
    
    if request.method == 'GET':
        request.form.name = course.name
    elif request.method == 'POST':
        # email validation
        other_course = Course.query.filter(Course.name == request.form['name'] ).first()
        if (other_course is not None) and (other_course.id != course.id):
            course.user_ids = request.form.getlist('users') # keeps appropriate users selected
            error_msg = "This course name is already being used"
            flash('This course name is already being used!!', 'error')
        else:
            course.name  = request.form['name']
            db.session.add(course)
            db.session.commit()
            flash('Course Created!!', 'success')
            return redirect(url_for('admin.admin_list_courses'))
    return render_template('admin/admin_create_edit_course.html', course=course, error_msg=error_msg, verb="Edit")



@admin_blueprint.route('/admin/delete_course/<course_id>')
@roles_required('admin')  
def admin_delete_course(course_id):
    course = Course.query.filter(Course.id == course_id).first()
    db.session.delete(course)
    db.session.commit()
    flash('Course Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_courses'))



#############################End Course Views#######################################
####################################################################################

####################################################################################
#############################Language Views###########################################

@admin_blueprint.route('/admin/list_languages', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_list_languages():
    languages = Language.query.order_by(Language.name.asc())
    for language in languages:
        print(language.name)
    return render_template('admin/admin_list_languages.html', languages=languages) 

@admin_blueprint.route('/admin/create_language', methods=['GET', 'POST'])
@roles_required('admin')  
def admin_create_language():
    error_msg = ""
    language = Language()

    if request.method == 'POST':
        # email validation
        other_language = Language.query.filter(Language.name == request.form['name'] ).first()
        if (other_language is not None) and (other_language.id != language.id):
            # language.user_ids = request.form.getlist('users') # keeps appropriate users selected
            error_msg = "This language name is already being used"
            flash('This language name is already being used!!', 'error')
        else:
            language.name  = request.form['name']
            db.session.add(language)
            db.session.commit()
            flash('Language Created!!', 'success')
            return redirect(url_for('admin.admin_list_languages'))
    return render_template('admin/admin_create_edit_language.html', language=language, error_msg=error_msg, verb="Create")



@admin_blueprint.route('/admin/edit_language/<language_id>', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_edit_language(language_id):
    error_msg=""
    language = Language.query.filter(Language.id == language_id).first()
    
    if request.method == 'GET':
        request.form.name = language.name
    elif request.method == 'POST':
        # email validation
        other_language = Language.query.filter(Language.name == request.form['name'] ).first()
        if (other_language is not None) and (other_language.id != language.id):
            language.user_ids = request.form.getlist('users') # keeps appropriate users selected
            error_msg = "This language name is already being used"
            flash('This language name is already being used!!', 'error')
        else:
            language.name  = request.form['name']
            db.session.add(language)
            db.session.commit()
            flash('Language Created!!', 'success')
            return redirect(url_for('admin.admin_list_languages'))
    return render_template('admin/admin_create_edit_language.html', language=language, error_msg=error_msg, verb="Edit")



@admin_blueprint.route('/admin/delete_language/<language_id>')
@roles_required('admin')  
def admin_delete_language(language_id):
    language = Language.query.filter(Language.id == language_id).first()
    db.session.delete(language)
    db.session.commit()
    flash('Language Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_languages'))



#############################End Language Views#######################################
####################################################################################



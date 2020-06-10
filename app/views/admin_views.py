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

@admin_blueprint.route('/admin/create_user', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_create_user():
    form = UserCustomForm()
    
    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices

    if form.validate_on_submit():
        user = User()
        user.first_name  = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.roles = []
        for role_id in form.roles.data:
            roleObj = Role.query.filter(Role.id == role_id).first()
            user.roles.append(roleObj)
        # todo: add in some password validations
        user.password=current_app.user_manager.password_manager.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('User Created!!', 'success')
        return redirect(url_for('admin.admin_list_users'))
    return render_template('admin/admin_create_user.html', form=form)

@admin_blueprint.route('/admin/create_tutor', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_create_tutor():
    form = TutorCustomForm()
    # form.first_name.data = "luke"
    # form.last_name.data = "fern"   
    # form.email.data="fern@weber.edu"
    # form.phone.data="8015409771"

    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices

    print(role_choices)
    if form.add_time.data:
        form.dates.append_entry()
        return render_template('admin/admin_create_tutor.html', form=form, state='add_time')

    if form.remove_time.data:
        print("DDDDDDDD", form.remove_time_id.data)
        print("xxxxxxx", type(form.dates), len(form.dates))

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
        print("popped_entry.data['id']", popped_entry.data['id'])
        if popped_entry.data['id']:
                child = Time.query.filter(Time.id == popped_entry.data['id']).first()
                db.session.delete(child)
                db.session.commit()

        return render_template('admin/admin_create_tutor.html', form=form, state='add_time')


    if form.validate_on_submit():
        user = User()
        user.first_name  = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.roles = []
        for role_id in form.roles.data:
            roleObj = Role.query.filter(Role.id == role_id).first()
            user.roles.append(roleObj)
        # todo: add in some password validations

        user.languages = []
        for lang in form.languages.data:
            print('dir(lang) dumps the attributes in the object: ', dir(lang) )
            print('lang.__dict__ dumps the attributes and values: :', lang.__dict__)
            langObj = Language.query.filter(Language.id == lang.id).first()
            user.languages.append(langObj)

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
            print(date_group['time_day'].data, date_group['time_start'].data, date_group['time_end'].data)
            time = Time()
            time.time_day = date_group['time_day'].data
            time.time_start = date_group['time_start'].data
            time.time_end = date_group['time_end'].data
            time.tutor_id = tutor.id
            db.session.add(time)
            db.session.commit()



        flash('User Created!!', 'success')
        return redirect(url_for('admin.admin_list_users'))
    return render_template('admin/admin_create_tutor.html', form=form)

@admin_blueprint.route('/admin/edit_tutor/<user_id>', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_edit_tutor(user_id):
    user = User.query.filter(User.id == user_id).first()
    
    print("XXXXXXXXXXXXXXXXXXXXX:")
    print(user.first_name)

    # determining the default options to be selected (notice how they are loaded when the form is instantiated)
    current_roles = []
    for role in user.roles:
        current_roles.append(str(role.id))

    form = TutorCustomForm(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email, 
    roles=current_roles, phone=user.tutor.tutor_phone, display_in_sched=user.tutor.display_in_sched, dates=user.tutor.dates)

    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices

    if form.add_time.data:
        form.dates.append_entry()
        return render_template('admin/admin_edit_tutor.html', form=form)

    if form.remove_time.data:
        print("DDDDDDDD", form.remove_time_id.data)
        print("xxxxxxx", type(form.dates), len(form.dates))

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
        print("popped_entry.data['id']", popped_entry.data['id'])
        if popped_entry.data['id']:
                child = Time.query.filter(Time.id == popped_entry.data['id']).first()
                db.session.delete(child)
                db.session.commit()

        return render_template('admin/admin_edit_tutor.html', form=form)

    if form.validate_on_submit():
        user.first_name  = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.roles = []
        for role_id in form.roles.data:
            roleObj = Role.query.filter(Role.id == role_id).first()
            user.roles.append(roleObj)
        if form.password.data != "":
            user.password=current_app.user_manager.password_manager.hash_password(form.password.data)

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
    return render_template('admin/admin_edit_tutor.html', form=form)



@admin_blueprint.route('/admin/edit_user/<user_id>', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_edit_user(user_id):
    user = User.query.filter(User.id == user_id).first()

    # see "secret sauce" at https://stackoverflow.com/questions/12099741/how-do-you-set-a-default-value-for-a-wtforms-selectfield
    # to have a particular option selected in a selectlist, the option has to be loaded into the form when it is first instantiated
    # likewise to have multiple options selected in a multipleselectlist the options have to be loaded into the form when it is first instantiated
    # the syntax for setting the selects varies:
    # selectlist example:  form = MyUserForm(roles=1) #the first option is preselected
    # selectmultiplelist example: form = MyUserForm(roles=[1,3]) #the first and third option are preselected
    
    # determining the default options to be selected (notice how they are loaded when the form is instantiated)
    current_roles = []
    for role in user.roles:
        current_roles.append(str(role.id))

    form = UserCustomForm(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email, roles=current_roles)

    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices


    if form.validate_on_submit():
        user.first_name  = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.roles = []
        for role_id in form.roles.data:
            roleObj = Role.query.filter(Role.id == role_id).first()
            user.roles.append(roleObj)
        if form.password.data != "":
            user.password=current_app.user_manager.password_manager.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User Updated!!', 'success')
        return redirect(url_for('admin.admin_list_users'))
    return render_template('admin/admin_edit_user.html', form=form)


@admin_blueprint.route('/admin/delete_user/<user_id>')
@roles_required('admin')  
def admin_delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash('User Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_users'))

@admin_blueprint.route('/admin/create_role', methods=['GET', 'POST'])
@roles_required('admin')  
def admin_create_role():
    form = RoleCustomForm()

    if form.validate_on_submit():
        role = Role()
        role.name  = form.name.data
        # role.label = form.label.data
        db.session.add(role)
        db.session.commit()
        flash('Role Created!!', 'success')
        return redirect(url_for('admin.admin_list_roles'))
    return render_template('admin/admin_create_role.html', form=form)


@admin_blueprint.route('/admin/list_roles', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_list_roles():
    roles = Role.query.order_by(Role.name.asc())
    for role in roles:
        print(role.name)
    return render_template('admin/admin_list_roles.html', roles=roles) 



@admin_blueprint.route('/admin/delete_role/<role_id>')
@roles_required('admin')  
def admin_delete_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    db.session.delete(role)
    db.session.commit()
    flash('Role Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_roles'))



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
    return render_template('admin/admin_edit_role.html', form=form)


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
    # users = User.query.join(UsersRoles).join(Role).filter(Role.name == 'student').all()

    if request.method == 'POST':
        # email validation
        other_course = Course.query.filter(Course.name == request.form['name'] ).first()
        if (other_course is not None) and (other_course.id != course.id):
            # course.user_ids = request.form.getlist('users') # keeps appropriate users selected
            error_msg = "This course name is already being used"
            flash('This course name is already being used!!', 'error')
        else:
            course.name  = request.form['name']
            # course.users = []
            # for user_id in request.form.getlist('users'):
            #     userObj = User.query.filter(User.id == user_id).first()
            #     course.users.append(userObj)
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
    # users = User.query.join(UsersRoles).join(Role).filter(Role.name == 'student').all()

    

    # using user.roles creates complications. so we make a new attribute instead. this
    # is used in the form to select what roles are associated with the user
    # course.user_ids = []
    # for user in course.users:
    #     course.user_ids.append(str(user.id))
    
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
            # course.users = []
            # for user_id in request.form.getlist('users'):
            #     userObj = User.query.filter(User.id == user_id).first()
            #     course.users.append(userObj)
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
    # users = User.query.join(UsersRoles).join(Role).filter(Role.name == 'student').all()

    if request.method == 'POST':
        # email validation
        other_language = Language.query.filter(Language.name == request.form['name'] ).first()
        if (other_language is not None) and (other_language.id != language.id):
            # language.user_ids = request.form.getlist('users') # keeps appropriate users selected
            error_msg = "This language name is already being used"
            flash('This language name is already being used!!', 'error')
        else:
            language.name  = request.form['name']
            # language.users = []
            # for user_id in request.form.getlist('users'):
            #     userObj = User.query.filter(User.id == user_id).first()
            #     language.users.append(userObj)
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
    # users = User.query.join(UsersRoles).join(Role).filter(Role.name == 'student').all()

    

    # using user.roles creates complications. so we make a new attribute instead. this
    # is used in the form to select what roles are associated with the user
    # language.user_ids = []
    # for user in language.users:
    #     language.user_ids.append(str(user.id))
    
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
            # language.users = []
            # for user_id in request.form.getlist('users'):
            #     userObj = User.query.filter(User.id == user_id).first()
            #     language.users.append(userObj)
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

# the below views are for testing roles
# you must create teacher and student roles to test them
@admin_blueprint.route('/admin/teacher_or_admin')
@roles_required(['admin', 'teacher'])  # requires admin OR teacher role
def admin_teacher_or_admin():
    return "You have the right roles to access this page - it requires admin OR teacher roles"

@admin_blueprint.route('/admin/teacher_and_admin')
@roles_required('admin','teacher')  # requires admin AND teacher roles
def admin_teacher_and_admin():
    return "You have the right roles to access this view"

@admin_blueprint.route('/admin/student')
@roles_required('student')  
def admin_student():
    return "You have the right roles to access this page - requires student role"

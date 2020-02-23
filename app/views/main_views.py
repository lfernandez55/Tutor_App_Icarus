# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import User, Role
from app.forms.book_forms import BookForm
from app.forms.main_forms import UserProfileForm, UserCustomForm

main_blueprint = Blueprint('main', __name__, template_folder='templates')



# The Home page is accessible to anyone
@main_blueprint.route('/')
def home_page():
    return render_template('main/home_page.html')

# this is here just as model code for creating new views and forms
@main_blueprint.route('/foo')
def foo():
    bookForm = BookForm()
    return render_template('main/foo.html', bookForm = bookForm)


# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/member')
@login_required  # Limits access to authenticated users
def member_page():
    return render_template('main/user_page.html')


# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')


@main_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.home_page'))

    # Process GET or invalid POST
    return render_template('main/user_profile_page.html',
                           form=form)


# the following admin views list users, edit users, creat new users

# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin_list_users')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_list_users():
    users = User.query.all()
    return render_template('main/admin_list_users.html', users=users)


@main_blueprint.route('/admin_edit_user/<user_id>', methods=['GET', 'POST'] )
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
        db.session.add(user)
        db.session.commit()
        flash('User Updated!!', 'success')
        return redirect(url_for('main.admin_list_users'))
    return render_template('main/admin_edit_user.html', form=form)

@main_blueprint.route('/admin_delete_user/<user_id>')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash('User Deleted!!', 'success')
    return redirect(url_for('main.admin_list_users'))

@main_blueprint.route('/admin_create_roles')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_create_roles():

    new_roles = ['teacher','student']
    for new_role_name in new_roles:
        role = Role.query.filter(Role.name == new_role_name).first()
        if role == None:
            new_role = Role()
            new_role.name = new_role_name
            db.session.add(new_role)
            db.session.commit()
   
    roles = Role.query.all()
    role_message = ""
    for role in roles:
        role_message = role.name + ", " + role_message 
    role_message = "The following roles now exist in the db: " + role_message
    flash(role_message, 'success')
    return redirect(url_for('main.admin_page'))


@main_blueprint.route('/admin_create_user')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_create_user():
    return render_template('main/admin_create_user.html')

@main_blueprint.route('/admin_teacher_or_admin')
@roles_required(['admin', 'teacher'])  # requires admin OR teacher role
def admin_teacher_or_admin():
    return "You have the right roles to access this page - it requires admin OR teacher roles"

@main_blueprint.route('/admin_teacher_and_admin')
@roles_required('admin','teacher')  # required admin AND teacher roles
def admin_teacher_and_admin():
    return "You have the right roles to access this view"

@main_blueprint.route('/admin_student')
@roles_required('student')  
def admin_student():
    return "You have the right roles to access this page - requires student role"


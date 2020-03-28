from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for, current_app
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import User, Role, Tutor, Time
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

    # if form.add_child.data:
    #     # tutor_form = TutorCustomForm()
    #     form.children.append_entry()
    #     return render_template('admin/admin_create_user.html', form=form)

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

        # tutor = Tutor()
        # tutor.tutor_phone = form.tutor.data['phone']
        # tutor.user_id = user.id
        # db.session.add(tutor)
        # db.session.commit()

        flash('User Created!!', 'success')
        return redirect(url_for('admin.admin_list_users'))
    return render_template('admin/admin_create_user.html', form=form)

@admin_blueprint.route('/admin/create_tutor', methods=['GET', 'POST'] )
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_create_tutor():
    form = TutorCustomForm()
    form.first_name.data = "luke"
    form.last_name.data = "fern"   
    form.email.data="fern@weber.edu"
    form.phone.data="8015409771"

    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices

    print(role_choices)
    if form.add_child.data:
        form.dates.append_entry()
        return render_template('admin/admin_create_tutor.html', form=form)

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

        tutor = Tutor()
        tutor.tutor_phone = form.phone.data
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
    # the user.tutor doesn't have to be iterated through becuz in the model we defined it the backref as uselist='false'
    print(user.tutor.tutor_phone)
    print(user.tutor.dates)

    # determining the default options to be selected (notice how they are loaded when the form is instantiated)
    current_roles = []
    for role in user.roles:
        current_roles.append(str(role.id))

    form = TutorCustomForm(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email, 
    roles=current_roles, phone=user.tutor.tutor_phone, dates=user.tutor.dates)

    # adding the full set of select options to the select list (this is different than determining the default/selected options above)
    rolesCollection = Role.query.all()
    role_list = []
    for role in rolesCollection:
        role_list.append(role.name)
    role_choices = list(enumerate(role_list,start=1))
    form.roles.choices = role_choices

    if form.add_child.data:
        form.dates.append_entry()
        return render_template('admin/admin_create_tutor.html', form=form)

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
        for x, date_group in enumerate(form.dates):
            print(date_group['time_day'].data, date_group['time_start'].data, date_group['time_end'].data)
            if x < len(user.tutor.dates):
                user.tutor.dates[x].time_day = date_group['time_day'].data
                user.tutor.dates[x].time_start = date_group['time_start'].data
                user.tutor.dates[x].time_end = date_group['time_end'].data
            else:
                time = Time()
                time.time_day = date_group['time_day'].data
                time.time_start = date_group['time_start'].data
                time.time_end = date_group['time_end'].data
                time.tutor_id = user.tutor.id
                db.session.add(time)
                db.session.commit()
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

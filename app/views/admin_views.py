from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for, current_app
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import User, Role
from app.forms.admin_forms import UserCustomForm, RoleCustomForm

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

@admin_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('admin/admin_page.html')

@admin_blueprint.route('/admin_list_users', methods=['GET', 'POST'] )
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

@admin_blueprint.route('/admin_create_user', methods=['GET', 'POST'] )
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



@admin_blueprint.route('/admin_edit_user/<user_id>', methods=['GET', 'POST'] )
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


@admin_blueprint.route('/admin_delete_user/<user_id>')
@roles_required('admin')  
def admin_delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash('User Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_users'))

@admin_blueprint.route('/admin_create_role', methods=['GET', 'POST'])
@roles_required('admin')  
def admin_create_role():
    form = RoleCustomForm()

    if form.validate_on_submit():
        role = Role()
        role.name  = form.name.data
        role.label = form.label.data
        db.session.add(role)
        db.session.commit()
        flash('Role Created!!', 'success')
        return redirect(url_for('admin.admin_list_roles'))
    return render_template('admin/admin_create_role.html', form=form)


@admin_blueprint.route('/admin_list_roles', methods=['GET', 'POST'] )
@roles_required('admin')  
def admin_list_roles():
    roles = Role.query.order_by(Role.name.asc())
    for role in roles:
        print(role.name)
    return render_template('admin/admin_list_roles.html', roles=roles) 



@admin_blueprint.route('/admin_delete_role/<role_id>')
@roles_required('admin')  
def admin_delete_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    db.session.delete(role)
    db.session.commit()
    flash('Role Deleted!!', 'success')
    return redirect(url_for('admin.admin_list_roles'))



@admin_blueprint.route('/admin_edit_role/<role_id>', methods=['GET', 'POST'] )
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

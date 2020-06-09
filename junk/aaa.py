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
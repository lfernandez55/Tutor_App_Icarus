# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for, current_app, jsonify, json
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import User, Role, Tutor, Time, Course, Language
from app.forms.book_forms import BookForm
from app.forms.main_forms import UserProfileForm

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

# example url: http://127.0.0.1:2000/schedule
@main_blueprint.route('/schedule')
def schedule():
    return render_template('main/schedule.html')

# example url: http://127.0.0.1:2000/schedule_json?tutor=aaaa
@main_blueprint.route('/schedule_json', methods={'GET'})
def schedule_json():
    # minute 807 in https://scotch.io/bar-talk/processing-incoming-request-data-in-flask
    print('args:', request.args.get('skill_id')) 
    skill_id = request.args.get('skill_id')
    dayArray = [1, 2, 3, 4, 5, 6, 7]
    slotArray = []
    for day in dayArray:
        if "lang" in skill_id:
            lang_id = skill_id.split("_")[1]
            Time.query.join(Tutor).join(Language).filter(Time.time_day == day).filter(Tutor.display_in_sched.is_(True)).filter(Language.id == lang.id).order_by(Time.time_day)
        elif "course" in skill_id:
            course_id = skill_id.split("_")[1]
            slots = Time.query.join(Tutor).join(Course).filter(Time.time_day == day).filter(Tutor.display_in_sched.is_(True)).filter(Course.id == course.id).order_by(Time.time_day)
        else:
            slots = Time.query.join(Tutor).filter(Time.time_day == day).filter(Tutor.display_in_sched.is_(True)).order_by(Time.time_day)
        for slot in slots:
            slotObj = {}
            ts = str(slot.time_start)
            te = str(slot.time_end)
            slotObj = {"id":slot.tutor.id, 'day':slot.time_day, 'time_start':ts, 'time_end': te,  \
            'display': slot.tutor.display_in_sched, \
            'tutor_first_name': slot.tutor.users.first_name, 'tutor_last_name': slot.tutor.users.last_name}

            print(slotObj)
            slotArray.append(slotObj)
    return jsonify(slotArray)


@main_blueprint.route('/schedule_courses_langs', methods={'GET'})
def schedule_courses_langs():

    courses = Course.query.order_by(Course.name).all()
    languages = Language.query.order_by(Language.name).all()

    skillArray = []
    for course in courses:
        skillObj = {}
        skillObj = {"id":course.id, 'name':course.name, "value": "course_" + str(course.id)}
        skillArray.append(skillObj)
    for lang in languages:
        skillObj = {}
        skillObj = {"id":lang.id, 'name':lang.name, "value": "lang_" + str(lang.id)}
        skillArray.append(skillObj)
    return jsonify(skillArray)

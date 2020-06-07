# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for, current_app, jsonify, json
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import User, Role, Tutor, Time
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
    print('in check guess')
    # minute 807 in https://scotch.io/bar-talk/processing-incoming-request-data-in-flask
    print('args:', request.args.get('tutor_id')) 
    # print(request.json) #print out the json object to the console
    # print(request.json['guess']) #print out the guess to the console
    
    foo = Time.query.join(Tutor).filter(Tutor.display_in_sched.is_(True))
    print('DEBBBBBBBBBBBBBBBB:', foo)
    for x in foo:
        print(x)
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    dayArray = [1, 2, 3, 4, 5, 6, 7]
    slotArray = []
    for day in dayArray:
        slots = Time.query.join(Tutor).filter(Time.time_day == day).filter(Tutor.display_in_sched.is_(True))
        for slot in slots:
            slot.overlap = False
            for otherSlot in slots:
                if slot.id != otherSlot.id:
                    if (slot.time_start <= otherSlot.time_end) and (slot.time_end >= otherSlot.time_start):
                        slot.overlap = True
            # slotObj = {'day':slot.time_day, 'time_start':slot.time_start, 'time_end': slot.time_end}
            # slotObj = {'day':slot.time_day}
            # print('debug', json.dumps(slot, indent=4, sort_keys=True, default=str))
            # jsonifiedSlot = json.dumps(slot, indent=4, sort_keys=True, default=str)
            # slotArray.append(jsonifiedSlot)
            slotObj = {}
            # slotObj['time_day'] = slot.time_day
            # slotObj['time_start'] = json.dumps(slot.time_start, indent=4, sort_keys=True, default=str)
            # slotObj['time_start'] = json.dumps(slot.time_end, indent=4, sort_keys=True, default=str)
            # ts = json.dumps(slot.time_start, indent=4, sort_keys=True, default=str)
            # te = json.dumps(slot.time_end, indent=4, sort_keys=True, default=str)
            ts = str(slot.time_start)
            te = str(slot.time_end)
            slotObj = {'day':slot.time_day, 'time_start':ts, 'time_end': te, 'overlap': slot.overlap, \
            'display': slot.tutor.display_in_sched, \
            'tutor_first_name': slot.tutor.users.first_name, 'tutor_last_name': slot.tutor.users.last_name}

            # this next line does not work: time_start is not serializable:
            # slotObj = {'day':slot.time_day, 'time_start':slot.time_start, 'time_end': slot.time_end}

            print(slotObj)
            slotArray.append(slotObj)
    # print(slotArray)
    # jsonifiedObj = json.dumps(slotArray, indent=4, sort_keys=True, default=str)
    return jsonify(slotArray)

    # hint = { "firstname":"Joe", "age":23} #create the hint as a dict
    # print("the hint:", hint) #print out the hint to the console
    # return jsonify(hint) #return the dict as a json

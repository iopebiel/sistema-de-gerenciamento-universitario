from flask import redirect, render_template, session
from app import closePostgresConnection, getPostgresConnection
from app.utils import fetchAllSubjects, fetchUserHeaderInformations, fetchAllTasks, getStudentIdByEmail
from flask import Blueprint

homeView = Blueprint('homeView', __name__, template_folder='../templates', static_folder='../static')


@homeView.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')

    user_email = session['user']
    user_info = fetchUserHeaderInformations(user_email)

    if not user_info:
        return redirect('/login')

    subjects = fetchAllSubjects(user_email)

    active_subjects = [subject for subject in subjects if subject['active']]


    student_id = getStudentIdByEmail(user_email)

    tasks = fetchAllTasks(student_id)

    return render_template('/home.html',
                           user=user_info,
                           subjects=active_subjects,
                           tasks=tasks)
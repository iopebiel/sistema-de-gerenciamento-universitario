from flask import redirect, render_template, session
from app import closePostgresConnection, getPostgresConnection
from app.utils import fetchAllSubjects, fetchAllTasks, fetchUserHeaderInformations
from flask import Blueprint

task = Blueprint('task', __name__, template_folder='../templates', static_folder='../static')

@task.route('/task')
def get_tasks():
    if 'user' not in session:
        return redirect('/login')

    student_email = session['user']
    student_info = fetchUserHeaderInformations(student_email)

    if student_info:
        student_name, student_course = student_info['name'], student_info['course']
        subjects = fetchAllSubjects(student_email)

        tasks = []
        for subject in subjects:
            tasks.append(fetchAllTasks(student_info['id'], subject['id']))

        return render_template('/pendente/task.html', name=student_name, course=student_course, email=student_email,
                               subjects=subjects, tasks=tasks)


@task.route('/insights')
def get_insights():
    if 'user' not in session:
        return redirect('/login')

    student_email = session['user']
    student_info = fetchUserHeaderInformations(student_email)

    if student_info:
        student_name, student_course = student_info['name'], student_info['course']
        return render_template('/pendente/insights.html', email=student_email, name=student_name, course=student_course)
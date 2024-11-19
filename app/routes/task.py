from datetime import datetime

from flask import Blueprint
from flask import redirect, render_template, session, flash, request

from app import closePostgresConnection, getPostgresConnection, db
from app.model import Task
from app.utils import fetchAllSubjects, fetchAllTasks, fetchUserHeaderInformations, getStudentIdByEmail

task = Blueprint('task', __name__, template_folder='../templates', static_folder='../static')

@task.route('/task')
def get_tasks():
    if 'user' not in session:
        return redirect('/login')

    student_email = session['user']
    student_info = fetchUserHeaderInformations(student_email)

    if student_info:
        student_id = getStudentIdByEmail(student_email)
        subjects = fetchAllSubjects(student_email)


        tasks = fetchAllTasks(student_id)

        return render_template('/task.html', user_info=student_info, tasks=tasks)

@task.route('/task/add', methods=['GET', 'POST'])
def task_add():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        task_title = request.form['title']
        studentsubject_id = request.form['studentsubjectid']
        insertion_date = datetime.now()
        deadline = request.form['deadline']
        description = request.form['description']

        connection_bd = getPostgresConnection()
        cursor_bd = connection_bd.cursor()

        new_task = Task(
            title=task_title, studentsubjectid=studentsubject_id, insertiondate=insertion_date, deadline=deadline, description=description, complete=False
       )
        try:
            db.session.add(new_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Erro ao salvar no banco de dados: " + str(e), "danger")
            return redirect('/task')

        cursor_bd.execute('SELECT id FROM task WHERE studentsubjectid = %s OR title = %s', (studentsubject_id, task_title))
        task_id = cursor_bd.fetchone()
        closePostgresConnection(connection_bd, cursor_bd)

        user_info = fetchUserHeaderInformations(session['user'])
        return redirect('/task')

    user_info = fetchUserHeaderInformations(session['user'])
    subjects = fetchAllSubjects(session['user'])
    return render_template('/taskAdd.html', user_info=user_info, subjects=subjects)


@task.route('/task/archive', methods=['POST'])
def task_complete():
    if 'user' not in session:
        return redirect('/login')

    task_id = request.form['selectedTask']
    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()

    cursor_bd.execute('UPDATE task SET complete = True WHERE id = %s', task_id)
    connection_bd.commit()

    closePostgresConnection(connection_bd, cursor_bd)
    flash('Disciplina arquivada com sucesso.', 'success')

    return redirect('/task')


@task.route('/task/update', methods=['POST'])
def task_update():
    if 'user' not in session:
        return redirect('/login')

    task_id = request.form['id']
    task_title = request.form['title']
    deadline = request.form['deadline']
    grade = request.form['grade']
    description = request.form['description']
    complete = request.form['complete']

    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()

    cursor_bd.execute('''
        UPDATE task
        SET title = %s, deadline = %s, grade = %s, description = %s, complete = %s
        WHERE id = %s
    ''', (task_title, deadline, grade, description, complete, task_id))

    connection_bd.commit()
    closePostgresConnection(connection_bd, cursor_bd)

    flash('Tarefa atualizada com sucesso.', 'success')
    return redirect('/task')

#
# @task.route('/insights')
# def get_insights():
#     if 'user' not in session:
#         return redirect('/login')
#
#     student_email = session['user']
#     student_info = fetchUserHeaderInformations(student_email)
#
#     if student_info:
#         student_name, student_course = student_info['name'], student_info['course']
#         return render_template('/insights.html', email=student_email, name=student_name, course=student_course)
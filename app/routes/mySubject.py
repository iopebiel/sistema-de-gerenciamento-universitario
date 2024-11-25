from flask import Blueprint
from flask import render_template, request, session, redirect, flash

from app.model import Subject, db
from ..utils import checkRecordStudentSubject, fetchAllSubjects, getPostgresConnection, closePostgresConnection, \
    fetchUserHeaderInformations, getStudentIdByEmail

mySubject = Blueprint('mySubject', __name__, template_folder='../templates', static_folder='../static')

@mySubject.route('/mySubject')
def subject():
    if 'user' not in session:
        return redirect('/login')

    email = session.get('user')
    user_info = fetchUserHeaderInformations(email)

    if user_info:
        subjects = fetchAllSubjects(email)
        return render_template('/mySubject.html', user_info=user_info, subjects=subjects)


@mySubject.route('/mySubject/add', methods=['GET', 'POST'])
def subject_add():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        subject_name = request.form['name']
        subject_code = request.form['code']
        teacher = request.form['teacher']
        day_of_week = request.form['day']
        schedule = request.form['schedule']
        classes_per_day = int(request.form.get('option'))
        total_classes = classes_per_day * 19

        user_email = session['user']
        user_info = fetchUserHeaderInformations(user_email)

        connection_bd = getPostgresConnection()
        cursor_bd = connection_bd.cursor()

        cursor_bd.execute('SELECT id FROM subject WHERE code = %s OR name = %s', (subject_code, subject_name))
        existing_subject_id = cursor_bd.fetchone()

        if existing_subject_id:
            checkRecordStudentSubject(user_email, existing_subject_id)
        else:
            new_subject = Subject(
                code=subject_code, name=subject_name, teacher=teacher, course=user_info['course'],
                day=day_of_week, schedule=schedule, classesperday=classes_per_day, totalclasses=total_classes
            )
            try:
                db.session.add(new_subject)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash("Erro ao salvar no banco de dados: " + str(e), "danger")
                return redirect('/mySubject')

            cursor_bd.execute('SELECT id FROM subject WHERE code = %s OR name = %s', (subject_code, subject_name))
            subject_id = cursor_bd.fetchone()
            closePostgresConnection(connection_bd, cursor_bd)

            checkRecordStudentSubject(user_email, subject_id)

    user_info = fetchUserHeaderInformations(session['user'])
    return render_template('/subjectAdd.html', email=session['user'], name=user_info['name'], course=user_info['course'])


@mySubject.route('/mySubject/archive', methods=['POST'])
def subject_delete():
    if 'user' not in session:
        return redirect('/login')

    subject_id = request.form['selectedSubject']
    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()
    user_email = session['user']

    student_id = getStudentIdByEmail(user_email)

    cursor_bd.execute('UPDATE student_subject SET active = False WHERE studentid = %s AND subjectid = %s', (student_id, subject_id))
    connection_bd.commit()

    closePostgresConnection(connection_bd, cursor_bd)
    flash('Disciplina arquivada com sucesso.', 'success')

    return redirect('/mySubject')


@mySubject.route('/mySubject/update', methods=['POST'])
def subject_update():
    if 'user' not in session:
        return redirect('/login')

    subject_id = request.form['id']
    subject_name = request.form['name']
    subject_code = request.form['code']
    teacher= request.form['teacher']
    day_of_week = request.form['day']
    schedule = request.form['schedule']
    classes_per_day = int(request.form.get('option'))
    total_classes = classes_per_day * 19

    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()

    cursor_bd.execute('''
        UPDATE subject
        SET code = %s, name = %s, teacher= %s, day = %s, schedule = %s, classesperday = %s, totalclasses = %s
        WHERE id = %s
    ''', (subject_code, subject_name, teacher, day_of_week, schedule, classes_per_day, total_classes, subject_id))

    active = request.form['active'].lower() == 'true'

    user_email = session['user']
    student_id = getStudentIdByEmail(user_email)

    cursor_bd.execute('''
        UPDATE student_subject
        SET active = %s
        WHERE subjectid = %s AND studentid = %s
    ''', (active, subject_id, student_id))

    connection_bd.commit()
    closePostgresConnection(connection_bd, cursor_bd)

    flash('Disciplina atualizada com sucesso.', 'success')
    return redirect('/mySubject')

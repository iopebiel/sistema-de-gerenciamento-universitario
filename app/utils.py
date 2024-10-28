from datetime import datetime
import os
from flask import redirect, flash
from werkzeug.security import check_password_hash
import smtplib
from email.mime.text import MIMEText

from app import closePostgresConnection, getPostgresConnection
from app.model import StudentSubject, db

EMAIL_SGU = os.environ["EMAIL_ADRESS"]


def sendEmail(recipient, subject, body):
    smtpServer = os.environ["EMAIL_SERVER"]
    smtpPort = 587
    smtpUsername = EMAIL_SGU
    smtpPassword = os.environ["EMAIL_PASSWORD"]

    msg = MIMEText(body)
    msg['From'] = EMAIL_SGU
    msg['To'] = recipient
    msg['Subject'] = subject

    server = smtplib.SMTP(smtpServer, smtpPort)
    try:
        server.starttls()
        server.login(smtpUsername, smtpPassword)
        server.sendmail(smtpUsername, [recipient], msg.as_string())
        server.quit()

    except Exception as e:
        print(f"Ocorreu um erro ao enviar e-mail: {e}")

def fetchUserHeaderInformations(user_email):
    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()

    try:
        cursor_bd.execute(
            'SELECT name, course '
            'FROM student WHERE email = %s',
            (user_email,))
        user_profile = cursor_bd.fetchone()
    except Exception as e:
        print(f"Error fetching user data: {e}")
        user_profile = None

    closePostgresConnection(connection_bd, cursor_bd)

    if user_profile:
        user_data = {
            "name": user_profile[0],
            "course": user_profile[1]
        }
        return user_data
    else:
        return None


def getStudentIdByEmail(user_email):
    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()

    try:
        cursor_bd.execute(
            'SELECT id '
            'FROM student WHERE email = %s',
            (user_email,))
        user_id = cursor_bd.fetchone()
    except Exception as e:
        print(f"Erro ao obter ID do usuário {e}")
        user_id = None

    closePostgresConnection(connection_bd, cursor_bd)

    if user_id:
        return user_id[0]
    else:
        return None


def fetchAllUserData(user_email):
    connection_bd = getPostgresConnection()
    cursor_bd = connection_bd.cursor()

    try:
        cursor_bd.execute(
            'SELECT id, studentnumber, email, password, name, course, semester, classgroup, unit '
            'FROM student WHERE email = %s',
            (user_email,))
        user_profile = cursor_bd.fetchone()
    except Exception as e:
        print(f"Error fetching user data: {e}")
        user_profile = None

    closePostgresConnection(connection_bd, cursor_bd)

    if user_profile:
        user_data = {
            "id": user_profile[0],
            "record": user_profile[1],
            "email": user_profile[2],
            "password": user_profile[3],
            "name": user_profile[4],
            "course": user_profile[5],
            "semester": user_profile[6],
            "class": user_profile[7],
            "unit": user_profile[8]
        }
        return user_data
    else:
        return None


def fetchAllSubjects(student_email):
    connection = getPostgresConnection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM student WHERE email = %s', (student_email,))
    student_id = cursor.fetchone()

    if student_id is None:
        return []

    student_id = student_id[0]

    cursor.execute("""
        SELECT subjectid, active
        FROM student_subject
        WHERE studentid = %s
    """, (student_id,))
    results = cursor.fetchall()

    subject_data = []

    for row in results:
        subject_id, active = row

        cursor.execute("""
            SELECT *
            FROM subject
            WHERE id = %s
            ORDER BY
                CASE
                    WHEN day = 'Segunda-feira' THEN 1
                    WHEN day = 'Terça-feira' THEN 2
                    WHEN day = 'Quarta-feira' THEN 3
                    WHEN day = 'Quinta-feira' THEN 4
                    WHEN day = 'Sexta-feira' THEN 5
                    WHEN day = 'Sábado' THEN 6
                    ELSE 7
                END, schedule
        """, (subject_id,))

        subject = cursor.fetchone()

        if subject:
            id, code, name, teacher, course, day, schedule, classesperday, totalclasses = subject

            subject_object = {
                "id": id,
                "code": code,
                "name": name,
                "teacher": teacher,
                "course": course,
                "day": day,
                "schedule": schedule,
                "classesperday": classesperday,
                "totalclasses": totalclasses,
                "active": active
            }

            subject_data.append(subject_object)

    connection.close()

    return subject_data


def fetchAllTasks(student_id):
    connection = getPostgresConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, studentsubjectid, insertiondate, deadline, grade, description, active
        FROM task
        WHERE studentsubjectid IN (
            SELECT id
            FROM student_subject
            WHERE studentid = %s
        )
        ORDER BY deadline
    """, (student_id,))
    results = cursor.fetchall()

    task_data = []

    for row in results:
        id, name, studentsubjectid, insertiondate, deadline, grade, description, active = row

        task_object = {
            "id": id,
            "name": name,
            "studentsubjectid": studentsubjectid,
            "insertiondate": insertiondate,
            "deadline": deadline,
            "grade": grade,
            "description": description,
            "active": active
        }

        task_data.append(task_object)

    connection.close()

    return task_data


def checkRecordStudentSubject(student_email, subject_id):
    connection = getPostgresConnection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM student WHERE email = %s', (student_email,))
    student_id = cursor.fetchone()

    cursor.execute('''
        SELECT * FROM student_subject
        WHERE studentid = %s AND subjectid = %s
    ''', (student_id, subject_id))

    result = cursor.fetchone()

    closePostgresConnection(connection, cursor)

    if result:
        if result[0] != True:
            flash(
                f"O aluno com o email {student_email} já se encontra se encontra com matricula ativa em disciplina de id {subject_id}.")
        else:
            flash(
                f"O aluno com o email {student_email} já se encontra matriculado porém com situação não ativa em disciplina de id {subject_id}.")
    else:
        includeStudentSubject(student_email, subject_id)


def includeStudentSubject(student_email, subject_code):
    enrollment_date = datetime.now()

    connection = getPostgresConnection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM student WHERE email = %s', (student_email,))
    student_id = cursor.fetchone()[0]

    newStudentSubject = StudentSubject(
        studentid=student_id, subjectid=subject_code, enrollmentdate=enrollment_date, active=True
    )

    try:
        db.session.add(newStudentSubject)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Erro ao matricular aluno na disciplina. " + str(e), "danger")
        return redirect('/mySubject')
    closePostgresConnection(connection, cursor)

    flash('Matrícula na disciplina realizada com sucesso.', 'success')
    return redirect('/mySubject')


def checkPassword(new_password, confirm_password):
    return new_password == confirm_password


def checkCurrentPassword(email, old_password):
    connection = getPostgresConnection()
    cursor = connection.cursor()

    cursor.execute('SELECT password FROM student WHERE email = %s', (email,))
    password_hash = cursor.fetchone()

    closePostgresConnection(connection, cursor)

    if password_hash:
        return check_password_hash(password_hash[0], old_password)
    else:
        return False


def updatePasswordDatabase(email, new_password_hash):
    connection = getPostgresConnection()
    cursor = connection.cursor()

    cursor.execute('UPDATE student SET password = %s WHERE email = %s', (new_password_hash, email))

    connection.commit()

    closePostgresConnection(connection, cursor)

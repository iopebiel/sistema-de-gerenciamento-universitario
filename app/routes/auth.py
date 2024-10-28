import random
import re

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from app.model import Student, db
from app.utils import sendEmail, updatePasswordDatabase

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return render_template('login.html')

@auth.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        course = request.form['course']
        semester = int(request.form['semester'])
        classgroup = course + str(semester)
        unit = request.form['unit']
        student_number = request.form['student_number']

        if not re.match(r'^\d{7}$', student_number):
            flash("Número de prontuário inválido. Deve conter exatamente 7 caracteres.", "alert")
            return render_template('subscribe.html')

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            user_already_exists = Student.query.filter_by(email=email).first()
        except Exception as e:
            flash("Erro ao conectar ao banco de dados: " + str(e), "danger")
            return render_template('subscribe.html')

        if user_already_exists:
            flash("Erro durante o cadastro: Este email já está cadastrado.", "danger")
            return render_template('subscribe.html')

        new_user = Student(
            name=name, email=email, password=password_hash, course=course,
            classgroup=classgroup, semester=semester, unit=unit, studentnumber=student_number
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Erro ao salvar no banco de dados: " + str(e), "danger")
            return render_template('subscribe.html')

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('auth.login'))

    return render_template('subscribe.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            student = Student.query.filter_by(email=email).first()
        except Exception as e:
            flash("Erro ao buscar o aluno no banco de dados: " + str(e), "danger")
            return render_template('login.html')

        if student and check_password_hash(student.password, password):
            session['user'] = email
            return redirect("\home")
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")

    return render_template('login.html')


@auth.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            user_email = session.get('user')
            password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            updatePasswordDatabase(user_email, password_hash)
            flash("Senha alterada com sucesso.", "success")
            return redirect('/login')

        flash("As senhas não coincidem.", "danger")
        return render_template('changePassword.html', step='step3')

    return render_template('changePassword.html', step='step1')


@auth.route('/codeEmail', methods=['POST'])
def codeEmail():
    email = request.form.get('email')
    session['user'] = email
    verification_code = str(random.randint(100000, 999999))
    session['verification_code'] = verification_code

    sendEmail(email, 'Código de Verificação', f'''Olá!
Seu código de verificação é: {verification_code}
Acesse a página de verificação, insira seu código e redefina sua senha.
''')
    return render_template('changePassword.html', code=verification_code, step='step2')


@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
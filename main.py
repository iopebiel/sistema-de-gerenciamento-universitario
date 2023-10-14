import random
import smtplib
from email.mime.text import MIMEText
import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave_secreta"

verification_codes = {}

def criar_tabela_alunos():
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            numeroprontuario TEXT PRIMARY KEY,
            nome TEXT,
            email TEXT,
            senha TEXT,
            curso TEXT,
            semestre INTEGER,
            unidade TEXT,
            turma TEXT
        )
    ''')

    conexao.commit()
    conexao.close()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/cadastro', methods=['GET','POST'])
def cadastrar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        nome = request.form['nome']
        curso = request.form['curso']
        
        # Converta o valor do semestre para um número inteiro
        semestre = int(request.form['semestre'])
        
        # Calcule a turma como a junção de curso e semestre
        turma = curso + str(semestre)

        unidade = request.form['unidade']
         # Obtenha o número de prontuário do formulário
        numeroprontuario = request.form['numeroprontuario']

        # Valide o número de prontuário (deve conter exatamente 7 dígitos)
        if not re.match(r'^\d{7}$', numeroprontuario):
            return "Número de prontuário inválido. Deve conter exatamente 7 dígitos."

        senha_hash = generate_password_hash(senha, method='sha256')

        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        
        try:
            # Verifique se o email já existe no banco de dados
            cursor.execute('SELECT email FROM alunos WHERE email = ?', (email,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                flash("Este email já está cadastrado.", "danger")

            senha_hash = generate_password_hash(senha, method='sha256')

            cursor.execute('''
                        INSERT INTO alunos (nome, email, senha, curso, turma, semestre, unidade, numeroprontuario) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome, email, senha_hash, curso, turma, semestre, unidade, numeroprontuario))

            conexao.commit()
            return "Cadastro realizado com sucesso!"
        
        except Exception as e:
                return f"Erro durante o cadastro: {str(e)}"
        finally:
                conexao.close()

    # Se o método for GET, apenas renderize a página de cadastro
    return render_template('cadastro.html')
    


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Consultar o banco de dados para obter o hash da senha
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT senha FROM alunos WHERE email = ?', (email,))
        senha_hash = cursor.fetchone()

        if senha_hash and check_password_hash(senha_hash[0], senha):
            # Senha correta, autenticar o usuário
            session['usuario'] = email
            return redirect ('/inicio')
        else:
            # Credenciais inválidas, mostrar mensagem de erro
                flash("Credenciais inválidas. Tente novamente.", "danger")

    # Se o método for GET, apenas renderize a página de login
    return render_template('login.html')

@app.route('/codigo_email', methods=['POST'])
def codigo_email():
    email = request.form.get('email')
    codigo_verificacao = str(random.randint(100000, 999999))  # Gere o código de verificação
    verification_codes[email] = codigo_verificacao  # Armazene o código associado ao e-mail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = '...'
    smtp_password = '...'

    # Crie a mensagem de e-mail
    msg = MIMEText(f'Seu código de verificação: {codigo_verificacao}')
    msg['Subject'] = 'Código de Verificação'
    msg['From'] = 'gabriel.iope@aluno.ifsp.edu.br'
    msg['To'] = email

    # Conecte-se ao servidor SMTP e envie o e-mail
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail('...', [email], msg.as_string())
    server.quit()

   
@app.route('/redefinir_senha', methods=['GET','POST'])
def redefinir_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova-senha')
        
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        
        cursor.execute('UPDATE usuarios SET senha = ? WHERE email = ?', (nova_senha, email))
        conexao.commit()
        conexao.close()

        # Redirecione o usuário para uma página de sucesso
        return render_template('login.html')
        
    return render_template('redefinir_senha.html')

@app.route('/inicio')
def inicio():
    email = session['usuario']
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email,))
    usuario_info = cursor.fetchone()
    nome_usuario, curso_usuario = usuario_info
    
    return render_template('inicio.html', nome=nome_usuario, curso=curso_usuario)

@app.route('/perfil')
def perfil():
    usuario = current_user

    return render_template('perfil.html', usuario=usuario)

if __name__ == '__main__':
    criar_tabela_alunos()
    app.run(debug=True)
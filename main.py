from flask import Flask, flash, make_response, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 
import random
import smtplib
from email.mime.text import MIMEText
import re
import sqlite3
import requests


#APP FLASK

app = Flask(__name__, static_url_path='/static')

app.secret_key = "chave_secreta" #Chave para sessão.

email_contato = 'contato.sistemagu@gmail.com'


#-----BANCO DE DADOS-----
def createTableAlunos():
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

    
def createTableDisciplinas():
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            sigla TEXT PRIMARY KEY,
            nome TEXT,
            professor TEXT,
            curso TEXT,
            dia TEXT,
            horario TIME,
            aulaspordia INTEGER,
            total INTEGER
        )
    ''')

    conexao.commit()
    conexao.close()

def createTableAlunoDisciplina():
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aluno_disciplina (
            aluno_id INTEGER,
            disciplina_id INTEGER,
            data_inscricao TEXT,
            nota INTEGER,
            PRIMARY KEY (aluno_id, disciplina_id),
            FOREIGN KEY (aluno_id) REFERENCES alunos (id),
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
        )
    ''')

    conexao.commit()
    conexao.close()


#-----INDEX-----


@app.route('/')
def index():
    return render_template('login.html')


#-----ENVIO DE E-MAIL-----

def sendEmail(destinatario, assunto, corpo):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = email_contato
    
    github_url = 'https://raw.githubusercontent.com/iopebiel/SistemaAcademico/meu-novo-branch/static/config/senha.txt'

    try:
        response = requests.get(github_url)
        response.raise_for_status()  # Lança uma exceção se a solicitação não for bem-sucedida

        smtp_password = response.text.strip()
    
    except requests.RequestException as e:
        print(f"Ocorreu um erro ao acessar o arquivo no GitHub: {e}")

    # Criação da mensagem de e-mail
    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = email_contato
    msg['To'] = destinatario

    # Conexão ao servidor SMTP e envio do e-mail
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail('...', [destinatario], msg.as_string())
    server.quit()
 
 
#-----PRIMEIRAS TELAS-----
 
@app.route('/subscribe', methods=['GET','POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        nome = request.form['nome']
        curso = request.form['curso']
        
        semestre = int(request.form['semestre'])
        turma = curso + str(semestre)

        unidade = request.form['unidade']
        numeroprontuario = request.form['numeroprontuario']

        #Deve conter exatamente 7 caracteres
        if not re.match(r'^.{7}$', numeroprontuario):
            flash ("Número de prontuário inválido. Deve conter exatamente 7 caracteres.", "alert")
            
        senha_hash = generate_password_hash(senha, method='sha256')
        
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        try:
            cursor.execute('SELECT email FROM alunos WHERE email = ?', (email,))
            usuario_existente = cursor.fetchone()
            if usuario_existente:
                flash("Erro durante o cadastro: Este email já está cadastrado.", "danger")
                return render_template('subscribe.html')

            senha_hash = generate_password_hash(senha, method='sha256')
            cursor.execute('''
                        INSERT INTO alunos (nome, email, senha, curso, turma, semestre, unidade, numeroprontuario) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome, email, senha_hash, curso, turma, semestre, unidade, numeroprontuario))
            conexao.commit()        
            sendEmail(email, 'Cadastro realizado com sucesso!', f'Olá {nome}!', 'Seu cadastro foi realizado com sucesso!', 'Seja bem vindo ao Sistema de Gerenciamento Universitário.')
    
            flash("Cadastro realizado com sucesso!", "success")
        except Exception as e:
                flash(f"Erro durante o cadastro: Número de Prontuário já existe.", "danger")
        finally:
                conexao.close()

    # Método GET
    return render_template('subscribe.html')
    


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']


        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT senha FROM alunos WHERE email = ?', (email,))
        senha_hash = cursor.fetchone()

        if senha_hash and check_password_hash(senha_hash[0], senha): #(Senha correta)
            session['usuario'] = email
            return redirect ('/home')
        else:
                flash("Credenciais inválidas. Tente novamente.", "danger")

    return render_template('login.html')

#-----REDEFINIR SENHA-----


@app.route('/codeEmail', methods=['POST'])
def codeEmail():    
    email = request.form.get('email')
    session['usuario'] = email
    codigo_verificacao = str(random.randint(100000, 999999))
    session['codigo'] = codigo_verificacao  
    
    sendEmail(email, 'Código de Verificação', f'''Olá!
Seu código de verificação é: {codigo_verificacao}
Acesse a página de verificação, insira seu código e redefina sua senha.
''')
    return render_template('changePassword.html', codigo = codigo_verificacao, etapa='etapa2-form')

@app.route('/checkCode', methods=['POST'])    
def checkCode():
    codigoenviado = session.get('codigo')
    codigodigitado = request.form.get('codigo_usuario')
    if (codigoenviado == codigodigitado):
        return render_template('changePassword.html', etapa='etapa3-form')    
    return render_template('changePassword.html', etapa='etapa2-form')
   
@app.route('/changePassword', methods=['GET','POST'])
def changePassword():
    if request.method == 'POST':
        nova_senha = request.form['nova-senha']
        confirmar_senha = request.form['confirmar-senha']
        if (nova_senha ==  confirmar_senha):
            email_usuario = session.get('usuario')
            senha_hash = generate_password_hash(nova_senha, method='sha256')
            updatePasswordDatabase(email_usuario, senha_hash)
            flash("Senha alterada com sucesso.", "success")
            return redirect('/login')
        flash("As senhas não coincidem", "danger")
        return render_template('changePassword.html', etapa = 'etapa3-form')  
    
    return render_template('changePassword.html', etapa = 'etapa1-form')  


#-----LOGADO-----

@app.route('/home')
def home():
    email = session.get('usuario')  
    if email:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email,))
        usuario_info = cursor.fetchone()
        horarios = fetchAllDisciplinas(email)
        conexao.close()
        nome_usuario, curso_usuario = usuario_info
        return render_template('/pendente/home.html', nome=nome_usuario, curso=curso_usuario, email=email, horarios=horarios)
    else:
        #Usuário não logado
        return redirect('/login')


#-----PERFIL-----


@app.route('/profile')
def profile():
    email_usuario = session.get('usuario')  
    if email_usuario:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM alunos WHERE email = ?', (email_usuario,))
        dados_usuario = cursor.fetchone()
        conexao.close()
        return render_template('/pendente/profile.html', usuario=dados_usuario)
    else:
        #Usuário não logado
        return redirect('/login')

@app.route('/profile/update', methods=['POST'])
def updateProfile():
    email_usuario = session.get('usuario')
    if email_usuario:
        novo_nome = request.form.get('novoNome')
        novo_email = request.form.get('novoEmail')
        novo_curso = request.form.get('novoCurso')
        novo_semestre = request.form.get('novoSemestre')

        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('UPDATE alunos SET nome = ?, email = ?, curso = ?, semestre = ? WHERE email = ?',
                       (novo_nome, novo_email, novo_curso, novo_semestre, email_usuario))
        conexao.commit()
        conexao.close()

        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile'))
    else:
        #usuario não logado
        return redirect('/login')

@app.route('/profile/updatepassword', methods=['POST'])
def updatePassword():
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        if checkPassword(senha_atual, nova_senha, confirmar_senha):
            email_usuario = session.get('usuario')
            if checkCurrentPassword(email_usuario, senha_atual):
                nova_senha_hash = generate_password_hash(nova_senha, method='sha256')
                updatePasswordDatabase(email_usuario, nova_senha_hash)
                flash("Senha alterada com sucesso.", "success")
                return redirect('/profile')  
            else:
                flash("Senha atual incorreta. Tente novamente.", "danger")
        
        flash("As senhas não coincidem ou não atendem aos critérios.", "danger")

    return

#-----SENHAS-----

def checkPassword(senha_atual, nova_senha, confirmar_senha):
    return senha_atual and nova_senha == confirmar_senha  

def checkCurrentPassword(email, senha_atual):
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT senha FROM alunos WHERE email = ?', (email,))
    senha_hash = cursor.fetchone()[0]
    conexao.close()
    
    return check_password_hash(senha_hash, senha_atual)

def updatePasswordDatabase(email, nova_senha_hash):
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('UPDATE alunos SET senha = ? WHERE email = ?', (nova_senha_hash, email))
    conexao.commit()
    conexao.close()


#DISCIPLINAS

def fetchAllDisciplinas(email_aluno):
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT disciplina_id
        FROM aluno_disciplina
        WHERE aluno_id = ?
    """, (email_aluno,))
    disciplinas_ids = cursor.fetchall()

    # Use uma lista de compreensão para extrair os IDs das disciplinas
    disciplinas_ids = [row[0] for row in disciplinas_ids]
    
    # Consulta para obter informações sobre as disciplinas
    cursor.execute("""
        SELECT *
        FROM disciplinas
        WHERE sigla IN ({})
        ORDER BY
            CASE
                WHEN dia = 'Segunda-feira' THEN 1
                WHEN dia = 'Terça-feira' THEN 2
                WHEN dia = 'Quarta-feira' THEN 3
                WHEN dia = 'Quinta-feira' THEN 4
                WHEN dia = 'Sexta-feira' THEN 5
                WHEN dia = 'Sábado' THEN 6
                ELSE 8
            END, horario
    """.format(','.join(['?']*len(disciplinas_ids))), disciplinas_ids)

    dados_disciplinas = cursor.fetchall()

    conexao.close()

    return dados_disciplinas

@app.route('/subject')
def subject():
    email = session.get('usuario')
    if email:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email,))
        usuario_info = cursor.fetchone()
        nome_usuario, curso_usuario = usuario_info
        disciplinas = fetchAllDisciplinas(email)
        return render_template('/pendente/subject.html',  nome=nome_usuario, curso=curso_usuario, email=email, disciplinas=disciplinas)
        

def checkRecordAlunoDisciplina(email_aluno, codigo_disciplina):
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT * FROM aluno_disciplina
        WHERE aluno_id = ? AND disciplina_id = ?
    ''', (email_aluno, codigo_disciplina))
    resultado = cursor.fetchone()
    conexao.close()
        
    if resultado:
        print(f"O aluno com o email {email_aluno} já está registrado na disciplina com ID {codigo_disciplina}.")
    else:
        includeAlunoDisciplina(email_aluno, codigo_disciplina)

def includeAlunoDisciplina(email_aluno, codigo_disciplina):
    data_inscricao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO aluno_disciplina (aluno_id, disciplina_id, data_inscricao)
        VALUES (?, ?, ?)
    ''', (email_aluno, codigo_disciplina, data_inscricao))  
    conexao.commit()
    conexao.close()
    flash('Disciplina adicionada com sucesso.', 'success')
    return redirect('/subject')


@app.route('/subject/add', methods=['GET', 'POST'])
def subjectAdd():
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nome_disciplina = request.form['nome']
        codigo_disciplina = request.form['codigo']
        professor = request.form['professor']
        dia_semana = request.form['dia']
        horario = request.form['horario']
        aulas_por_dia = int(request.form.get('opcao'))

        conexao = sqlite3.connect('usuarios.db')
        cursordisciplina = conexao.cursor()

        email_usuario = session['usuario']
        
        cursordisciplina.execute('SELECT sigla FROM disciplinas WHERE sigla = ? OR nome = ?', (codigo_disciplina, nome_disciplina))
        disciplina_existente = cursordisciplina.fetchone()
        if disciplina_existente:
            checkRecordAlunoDisciplina(email_usuario, codigo_disciplina)
        else:
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO disciplinas (sigla, nome, professor, dia, horario, aulaspordia, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (codigo_disciplina, nome_disciplina, professor, dia_semana, horario, aulas_por_dia, aulas_por_dia*19))
            conexao.commit()
            conexao.close()
            checkRecordAlunoDisciplina(email_usuario, codigo_disciplina) 
        
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    email_usuario = session['usuario']
    cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email_usuario,))
    usuario_info = cursor.fetchone()
    nome_usuario, curso_usuario = usuario_info
    return render_template('/pendente/subjectAdd.html', email = email_usuario, nome = nome_usuario, curso = curso_usuario)  # Renderize a página de adição de disciplina


#-----PÁGINAS FUTURAS-----

@app.route('/insights')
def insights():
    email_usuario = session.get('usuario')  
    if email_usuario:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email_usuario,))
        usuario_info = cursor.fetchone()
        nome_usuario, curso_usuario = usuario_info
        return render_template('/pendente/insights.html', email = email_usuario, nome = nome_usuario, curso = curso_usuario)
    
    else:
        #Usuário não logado.
        return redirect('/login')

@app.route('/messages')
def messages():
    email_usuario = session.get('usuario')
    if email_usuario:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email_usuario,))
        usuario_info = cursor.fetchone()
        nome_usuario, curso_usuario = usuario_info
        return render_template('/pendente/messages.html', email = email_usuario, nome = nome_usuario, curso = curso_usuario)
    
    else:
        #Usuário não logado.
        return redirect('/login')


@app.route('/logout')
def logout():
    # Remova os dados da sessão que identificam o usuário como autenticado
    session.pop('usuario', None)
    # Crie uma resposta HTTP com cabeçalho de controle de cache
    response = make_response(redirect(url_for('login')))
    # Adicione o cabeçalho "no-store" para evitar o cache
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'  
    return response

        
        
#-----DEFAULT-----
        
if __name__ == '__main__':
    createTableAlunos()
    createTableDisciplinas()
    createTableAlunoDisciplina()
    app.run(debug=True)
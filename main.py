import random
import smtplib
from email.mime.text import MIMEText
import re
import sqlite3

from flask import Flask, flash, make_response, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='/static')
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

    
def criar_tabela_disciplinas():
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            codigo TEXT,
            descricao TEXT
        )
    ''')

    conexao.commit()
    conexao.close()

def criar_tabela_aluno_disciplina():
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
    email = session.get('usuario')  # Observe que estamos usando session.get() para evitar erros se o usuário não estiver logado.
    if email:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email,))
        usuario_info = cursor.fetchone()
        nome_usuario, curso_usuario = usuario_info
        return render_template('inicio.html', nome=nome_usuario, curso=curso_usuario, email=email)
    
    else:
        # Trate o caso em que o usuário não está logado, por exemplo, redirecione para a página de login.
        return redirect('/login')

@app.route('/perfil')
def perfil():
    email_usuario = session.get('usuario')  # Observe que estamos usando session.get() para evitar erros se o usuário não estiver logado.
    if email_usuario:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM alunos WHERE email = ?', (email_usuario,))
        dados_usuario = cursor.fetchone()
        conexao.close()

        if dados_usuario:
            return render_template('perfil.html', usuario=dados_usuario)
        else:
            # Trate o caso em que o usuário não foi encontrado, por exemplo, redirecione para uma página de erro.
            return render_template('erro.html')
    else:
        # Trate o caso em que o usuário não está logado, por exemplo, redirecione para a página de login.
        return redirect('/login')

@app.route('/atualizar_perfil', methods=['POST'])
def atualizar_perfil():
    if 'usuario' in session:
        email_usuario = session.get('usuario')  # Observe que estamos usando session.get() para evitar erros se o usuário não estiver logado.
        novo_nome = request.form.get('nome')
        novo_email = request.form.get('email')
        novo_curso = request.form.get('curso')
        novo_semestre = request.form.get('semestre')

        # Atualize os dados do perfil no banco de dados
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('UPDATE alunos SET nome = ?, email = ?, curso = ?, semestre = ? WHERE email = ?',
                       (novo_nome, novo_email, novo_curso, novo_semestre, email_usuario))
        conexao.commit()
        conexao.close()

        # Redirecione de volta para a página de perfil
        return redirect('/perfil')
    else:
        # Lide com o caso em que o usuário não está autenticado
        return redirect('/login')

@app.route('/atualizar_senha', methods=['POST'])
def alterar_senha():
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        # Valide as senhas e realize a alteração se todas as validações forem aprovadas
        if validar_senhas(senha_atual, nova_senha, confirmar_senha):
            # Obtenha o email do usuário logado (você deve implementar a lógica para obter isso)
            email_usuario = session.get('usuario')

            # Valide a senha atual no banco de dados
            if validar_senha_atual(email_usuario, senha_atual):
                # Hash da nova senha
                nova_senha_hash = generate_password_hash(nova_senha, method='sha256')

                # Atualize a senha no banco de dados
                atualizar_senha_no_banco_de_dados(email_usuario, nova_senha_hash)

                flash("Senha alterada com sucesso.", "success")
                return redirect('/perfil')  # Redirecione para a página de perfil
            else:
                flash("Senha atual incorreta. Tente novamente.", "danger")
        
        flash("As senhas não coincidem ou não atendem aos critérios de segurança.", "danger")

    return render_template('alterar_senha.html')  # Renderize a página de alteração de senha

# Função para validar as senhas
def validar_senhas(senha_atual, nova_senha, confirmar_senha):
    # Implemente suas regras de validação de senhas aqui
    return senha_atual and nova_senha == confirmar_senha  # Exemplo simples

# Função para validar a senha atual no banco de dados
def validar_senha_atual(email, senha_atual):
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT senha FROM alunos WHERE email = ?', (email,))
    senha_hash = cursor.fetchone()[0]
    conexao.close()
    
    return check_password_hash(senha_hash, senha_atual)

# Função para atualizar a senha no banco de dados
def atualizar_senha_no_banco_de_dados(email, nova_senha_hash):
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    cursor.execute('UPDATE alunos SET senha = ? WHERE email = ?', (nova_senha_hash, email))
    conexao.commit()
    conexao.close()

@app.route('/disciplina')
def disciplina():
    email = session.get('usuario')  # Observe que estamos usando session.get() para evitar erros se o usuário não estiver logado.
    if email:
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email,))
        usuario_info = cursor.fetchone()
        nome_usuario, curso_usuario = usuario_info
        return render_template('disciplina.html',  nome=nome_usuario, curso=curso_usuario, email=email)


@app.route('/disciplina/adicionar', methods=['GET', 'POST'])
def adicionar_disciplina():
    # Verifique se o usuário está logado
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Obtenha os dados do formulário
        nome_disciplina = request.form['nome_disciplina']
        dia_semana = request.form['dia_semana']
        horario = request.form['horario']
        # Aqui você pode adicionar validações e processamento dos dados, como verificar a validade do horário, etc.

        # Conecte-se ao banco de dados SQLite
        conexao = sqlite3.connect('usuarios.db')
        cursor = conexao.cursor()

        # Obtenha o email do usuário logado
        email_usuario = session['usuario']

        # Insira os dados da disciplina no banco de dados
        cursor.execute('''
            INSERT INTO disciplinas (email_usuario, nome_disciplina, dia_semana, horario)
            VALUES (?, ?, ?, ?)
        ''', (email_usuario, nome_disciplina, dia_semana, horario))

        # Commit para salvar as alterações
        conexao.commit()
        conexao.close()

        flash('Disciplina adicionada com sucesso.', 'success')
        return redirect('/disciplinas')  # Redirecione para a página de disciplinas após adicionar

    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()
    email_usuario = session['usuario']
    cursor.execute('SELECT nome, curso FROM alunos WHERE email = ?', (email_usuario,))
    usuario_info = cursor.fetchone()
    nome_usuario, curso_usuario = usuario_info
    return render_template('adicionar_disciplina.html', email = email_usuario, nome = nome_usuario, curso = curso_usuario)  # Renderize a página de adição de disciplina







def criar_tabela_disciplinas():
    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            codigo TEXT,
            descricao TEXT
        )
    ''')

    conexao.commit()
    conexao.close()

@app.route('/relatorio')
def relatorio():
    email = session.get('usuario')  # Observe que estamos usando session.get() para evitar erros se o usuário não estiver logado.
    if email:
        return render_template('relatorio.html')
    
    else:
        # Trate o caso em que o usuário não está logado, por exemplo, redirecione para a página de login.
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

        
if __name__ == '__main__':
    criar_tabela_alunos()
    criar_tabela_disciplinas()
    criar_tabela_aluno_disciplina()
    app.run(debug=True)
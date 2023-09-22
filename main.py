import sqlite3

from flask import Flask, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave_secreta"

conexao = sqlite3.connect('usuarios.db')
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        senha TEXT
    )
''')

conexao.commit()
conexao.close()


@app.route('/')
def index():
    return render_template('cadastro.html')


@app.route('/cadastro', methods=['POST'])
def cadastrar():
    email = request.form['email']
    senha = request.form['senha']
    senha_hash = generate_password_hash(senha, method='sha256')

    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute('INSERT INTO usuarios (email, senha) VALUES (?, ?)', (email, senha_hash))

    conexao.commit()
    conexao.close()

    return "Cadastro realizado com sucesso!"


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']

    conexao = sqlite3.connect('usuarios.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
    usuario = cursor.fetchone()

    conexao.close()

    if usuario and check_password_hash(usuario[2], senha):
        session['usuario'] = usuario[1]
        return render_template('opcoes.html')
    else:
        return "Credenciais inválidas"


if __name__ == '__main__':
    app.run(debug=True)

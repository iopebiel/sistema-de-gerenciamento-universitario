from flask import render_template, request, session, redirect, flash, url_for
from ..utils import checkCurrentPassword, checkPassword, getPostgresConnection, closePostgresConnection, \
    updatePasswordDatabase, fetchAllUserData, fetchUserHeaderInformations
from werkzeug.security import generate_password_hash
from flask import Blueprint

myProfile = Blueprint('myProfile', __name__, template_folder='../templates', static_folder='../static')

@myProfile.route('/myProfile')
def profile():
    user_email = session.get('user')

    if user_email:
        user_data = fetchAllUserData(user_email)

        if user_data:
            return render_template('/myProfile.html', user=user_data)
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@myProfile.route('/myProfile/update', methods=['POST'])
def updateProfile():
    user_email = session.get('user')
    if user_email:
        new_name = request.form.get('newName')
        new_email = request.form.get('newEmail')
        new_course = request.form.get('newCourse')
        new_semester = request.form.get('newSemester')

        user_info = fetchUserHeaderInformations(user_email)

        connection_bd = getPostgresConnection()
        cursor_bd = connection_bd.cursor()

        cursor_bd.execute('''
            UPDATE student 
            SET name = %s, email = %s, course = %s, semester = %s 
            WHERE email = %s
        ''', (new_name or user_info['name'], new_email or user_email, new_course or user_info['course'], new_semester, user_email))

        connection_bd.commit()

        closePostgresConnection(connection_bd, cursor_bd)

        flash('Perfil atualizado com sucesso!', 'success')

        return redirect(url_for('myProfile.profile'))
    else:
        return redirect('/login')


@myProfile.route('/myProfile/updatepassword', methods=['POST'])
def updatePassword():
    if request.method == 'POST':
        old_password = request.form['oldPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']

        if checkPassword(new_password, confirm_password):
            user_email = session.get('user')
            if checkCurrentPassword(user_email, old_password):
                new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
                updatePasswordDatabase(user_email, new_password_hash)
                flash("Senha alterada com sucesso.", "success")
                return redirect('/myProfile')
            else:
                flash("Senha atual incorreta. Tente novamente.", "danger")

        flash("As senhas não coincidem ou não atendem aos critérios.", "danger")

    return redirect('/myProfile')

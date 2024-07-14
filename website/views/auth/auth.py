from ...models.user import User
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from pathlib import Path
from ... import app
from os import path
from flask import session

auth = Blueprint('auth', __name__)

upload_images = path.join(Path(__file__).parents[2], "static", app.config['UPLOAD_FOLDER'])

@auth.route('/', methods=['GET', 'POST'])
def home():
    return render_template('autentikasi/login.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    login_user(user)
                    if user.role == "admin":
                        return redirect(url_for('admin.dashboard'))
                    elif user.role == "Mahasiswa":
                        return redirect(url_for('students.dashboard'))
                    elif user.role == "Dosen" and user.profile_relationship.position == "Wakil Dekan 2":
                        return redirect(url_for('wadek.dashboard'))
                    elif user.role == "Dosen" and user.profile_relationship.position == "Dosen":
                        return redirect(url_for('students.dashboard'))
                    elif user.role == "Dosen" and user.profile_relationship.position == "Staff Umum":
                        return redirect(url_for('wadek.dashboard'))
            session['login_error'] = 'Username atau Password salah.'
            return redirect(url_for('auth.login'))
        return render_template('autentikasi/login.html', user=current_user)
    except Exception as e:
        print(e)
        abort(404)

@auth.route('/clear_login_error', methods=['POST'])
def clear_login_error():
    session.pop('login_error', None)
    return '', 204

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

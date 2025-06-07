from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import Usuario
from . import main

@main.route('/')
def home():
    """Redirige a la página de login."""
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios."""
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['contraseña']
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and check_password_hash(usuario.contraseña, clave):
            if usuario.estado != 'activo':
                flash('Tu cuenta está inactiva. Contacta al administrador.')
                return redirect(url_for('main.login'))

            login_user(usuario)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciales inválidas')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario."""
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    """Muestra el panel principal del usuario autenticado."""
    return render_template('dashboard.html', usuario=current_user)

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from . import main

@main.route('/mi_perfil')
@login_required
def mi_perfil():
    """Muestra el perfil del usuario actual."""
    return render_template('perfil.html', usuario=current_user)

@main.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Permite al usuario editar su perfil."""
    if request.method == 'POST':
        current_user.nombre = request.form['nombre']
        current_user.telefono = request.form['telefono']
        current_user.direccion = request.form['direccion']
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('main.mi_perfil'))

    return render_template('editar_perfil.html', usuario=current_user)

@main.route('/perfil/contraseña', methods=['GET', 'POST'])
@login_required
def cambiar_contraseña():
    """Permite al usuario cambiar su contraseña."""
    if request.method == 'POST':
        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        if not check_password_hash(current_user.contraseña, actual):
            flash('Contraseña actual incorrecta.')
        elif nueva != confirmar:
            flash('La nueva contraseña no coincide.')
        else:
            current_user.contraseña = generate_password_hash(nueva)
            db.session.commit()
            flash('Contraseña actualizada exitosamente.')
            return redirect(url_for('main.mi_perfil'))

    return render_template('cambiar_contraseña.html')

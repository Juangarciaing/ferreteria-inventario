from flask import redirect, render_template, request, flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app import db
from app.models import Usuario
from . import main, rol_requerido

@main.route('/admin/registrar_usuario', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def registrar_usuario():
    """Permite al admin registrar un nuevo usuario."""
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        clave = request.form['contraseña']
        rol = request.form['rol']

        # Validaciones de unicidad
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado.')
        elif Usuario.query.filter_by(cedula=cedula).first():
            flash('La cédula ya está registrada.')
        else:
            nueva_clave = generate_password_hash(clave)
            nuevo_usuario = Usuario(
                nombre=nombre,
                cedula=cedula,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                contraseña=nueva_clave,
                rol=rol
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario registrado correctamente.')
            return redirect(url_for('main.dashboard'))

    return render_template('registrar_usuario.html')

@main.route('/usuarios')
@login_required
@rol_requerido('admin')
def listar_usuarios():
    """Lista todos los usuarios (solo admin)."""
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios, usuario=current_user)

@main.route('/usuarios/toggle/<int:id>', methods=['POST'])
@login_required
@rol_requerido('admin')
def cambiar_estado_usuario(id):
    """Activa o desactiva un usuario (solo admin)."""
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash('No puedes cambiar el estado de tu propio usuario.')
        return redirect(url_for('main.listar_usuarios'))

    usuario.estado = 'inactivo' if usuario.estado == 'activo' else 'activo'
    db.session.commit()
    flash(f"Usuario {'desactivado' if usuario.estado == 'inactivo' else 'activado'} correctamente.")
    return redirect(url_for('main.listar_usuarios'))

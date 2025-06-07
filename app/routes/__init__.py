from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user
from functools import wraps

main = Blueprint('main', __name__)

# --- Decorador para roles ---
def rol_requerido(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.rol not in roles:
                flash('Acceso no autorizado')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Importa los módulos de rutas para registrarlos en el blueprint
from . import auth, admin, productos, ventas, compras, reportes, perfil

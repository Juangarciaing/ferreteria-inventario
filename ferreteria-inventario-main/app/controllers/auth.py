"""
Controlador de autenticación (LEGACY - Migrado a usuario.py)
DEPRECATED: Este archivo mantiene compatibilidad con código legacy.
Se recomienda usar el nuevo controlador usuario.py con Clean Architecture.
"""
from flask import Blueprint, request
from app.utils import create_response, handle_error
from app.exceptions import BusinessLogicError, ValidationError
from app.infrastructure.di import get_container

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint de login (compatible con legacy)
    MIGRADO: Ver POST /api/usuarios/login en usuario.py
    """
    try:
        data = request.get_json()
        
        # Usar el nuevo LoginUseCase de Clean Architecture
        container = get_container()
        use_case = container.resolve('login_use_case')
        
        # Adaptar el campo 'username' del frontend a 'email'
        login_data = {
            'email': data.get('username') or data.get('email'),
            'password': data.get('password')
        }
        
        usuario = use_case.execute(login_data)
        
        # TODO: Generar JWT token si es necesario
        return create_response(
            data=usuario,
            message="Login exitoso"
        )
    except ValidationError as e:
        return handle_error(e)
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error al iniciar sesión: {str(e)}",
            status_code=500
        )

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint de registro (compatible con legacy)
    MIGRADO: Ver POST /api/usuarios/register en usuario.py
    Nota: Este endpoint NO requiere autenticación para mantener compatibilidad,
    pero se recomienda usar el nuevo endpoint que requiere admin.
    """
    try:
        data = request.get_json()
        
        # Usar el nuevo CreateUsuarioUseCase de Clean Architecture
        container = get_container()
        use_case = container.resolve('create_usuario_use_case')
        
        usuario = use_case.execute(data)
        
        return create_response(
            data=usuario,
            message="Usuario registrado exitosamente",
            status_code=201
        )
    except ValidationError as e:
        return handle_error(e)
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error al registrar usuario: {str(e)}",
            status_code=500
        )
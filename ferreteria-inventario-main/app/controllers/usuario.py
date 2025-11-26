"""
Controlador de Usuario - Clean Architecture
"""
from flask import Blueprint, request
from app.utils import create_response, handle_error, token_required
from app.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.infrastructure.di import get_container

usuario_bp = Blueprint('usuario', __name__, url_prefix='/api/usuarios')


@usuario_bp.route('/register', methods=['POST'])
@token_required
def register_usuario(current_user):
    """
    Registrar nuevo usuario (solo admin)
    ---
    POST /api/usuarios/register
    Body: {nombre, email, password, rol, telefono?, direccion?}
    Response: {id, nombre, email, rol, ...} (sin password)
    """
    try:
        # Solo admin puede registrar usuarios
        if not current_user.get('rol') == 'admin':
            return create_response(
                message="No tienes permisos para registrar usuarios",
                status_code=403
            )
        
        data = request.get_json()
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


@usuario_bp.route('/login', methods=['POST'])
def login():
    """
    Login de usuario (sin autenticación previa)
    ---
    POST /api/usuarios/login
    Body: {email, password}
    Response: {token?, usuario: {id, nombre, email, rol, ...}}
    """
    try:
        data = request.get_json()
        container = get_container()
        use_case = container.resolve('login_use_case')
        
        usuario = use_case.execute(data)
        
        # TODO: Generar JWT token aquí si es necesario
        # from app.utils.jwt_utils import generate_token
        # token = generate_token(usuario)
        # return create_response(data={'token': token, 'usuario': usuario}, ...)
        
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


@usuario_bp.route('/<int:usuario_id>', methods=['GET'])
@token_required
def get_usuario(current_user, usuario_id):
    """
    Obtener usuario por ID
    ---
    GET /api/usuarios/:id
    Response: {id, nombre, email, rol, ...}
    """
    try:
        container = get_container()
        use_case = container.resolve('get_usuario_use_case')
        
        usuario = use_case.execute(usuario_id)
        
        return create_response(data=usuario)
    except NotFoundError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error al obtener usuario: {str(e)}",
            status_code=500
        )


@usuario_bp.route('', methods=['GET'])
@token_required
def get_all_usuarios(current_user):
    """
    Obtener todos los usuarios (con filtro opcional)
    ---
    GET /api/usuarios?only_active=true
    Response: [{id, nombre, email, rol, ...}]
    """
    try:
        # Solo admin puede ver todos los usuarios
        if not current_user.get('rol') == 'admin':
            return create_response(
                message="No tienes permisos para ver usuarios",
                status_code=403
            )
        
        only_active = request.args.get('only_active', 'false').lower() == 'true'
        
        container = get_container()
        use_case = container.resolve('get_all_usuarios_use_case')
        
        usuarios = use_case.execute(only_active=only_active)
        
        return create_response(data=usuarios)
    except Exception as e:
        return create_response(
            message=f"Error al obtener usuarios: {str(e)}",
            status_code=500
        )


@usuario_bp.route('/<int:usuario_id>', methods=['PUT'])
@token_required
def update_usuario(current_user, usuario_id):
    """
    Actualizar usuario (admin o el mismo usuario)
    ---
    PUT /api/usuarios/:id
    Body: {nombre?, email?, rol?, telefono?, direccion?, activo?, estado?}
    Response: {id, nombre, email, rol, ...}
    """
    try:
        print(f"\n{'='*80}")
        print(f"[CONTROLLER_UPDATE] Usuario actual: {current_user.get('nombre')} (Rol: {current_user.get('rol')})")
        print(f"[CONTROLLER_UPDATE] Actualizando usuario ID: {usuario_id}")
        
        # Solo admin o el mismo usuario puede actualizar
        if not (current_user.get('rol') == 'admin' or current_user.get('id') == usuario_id):
            return create_response(
                message="No tienes permisos para actualizar este usuario",
                status_code=403
            )
        
        data = request.get_json()
        print(f"[DEBUG] 📦 Datos RAW recibidos: {data}")
        
        # 🔄 MAPEO: Convertir 'estado' (frontend) a 'activo' (backend)
        if 'estado' in data:
            estado_valor = data['estado']
            print(f"[DEBUG] 🔄 Campo 'estado' detectado: {estado_valor} (tipo: {type(estado_valor).__name__})")
            
            # Convertir boolean a integer (0 o 1)
            data['activo'] = 1 if estado_valor else 0
            print(f"[DEBUG] ✅ Convertido a 'activo': {data['activo']}")
            
            data.pop('estado')  # Remover 'estado' del diccionario
            print(f"[DEBUG] 🗑️  Campo 'estado' eliminado del diccionario")
        
        print(f"[DEBUG] 📦 Datos después del mapeo: {data}")
        
        # Solo admin puede cambiar rol y estado activo
        if current_user.get('rol') != 'admin':
            print(f"[DEBUG] ⚠️  Usuario NO es admin, removiendo 'rol' y 'activo'")
            data.pop('rol', None)
            data.pop('activo', None)
        else:
            print(f"[DEBUG] ✅ Usuario ES admin, puede cambiar cualquier campo")
        
        print(f"[DEBUG] 📦 Datos FINALES a enviar al use case: {data}")
        
        container = get_container()
        use_case = container.resolve('update_usuario_use_case')
        
        usuario = use_case.execute(usuario_id, data)
        
        print(f"[DEBUG] ✅ Usuario actualizado exitosamente")
        print(f"{'='*80}\n")
        
        return create_response(
            data=usuario,
            message="Usuario actualizado exitosamente"
        )
    except ValidationError as e:
        return handle_error(e)
    except NotFoundError as e:
        return handle_error(e)
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        print(f"[DEBUG] ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_response(
            message=f"Error al actualizar usuario: {str(e)}",
            status_code=500
        )


@usuario_bp.route('/<int:usuario_id>', methods=['DELETE'])
@token_required
def delete_usuario(current_user, usuario_id):
    """
    Eliminar/desactivar usuario (solo admin)
    ---
    DELETE /api/usuarios/:id
    Response: {message}
    """
    try:
        # Solo admin puede eliminar usuarios
        if not current_user.get('rol') == 'admin':
            return create_response(
                message="No tienes permisos para eliminar usuarios",
                status_code=403
            )
        
        container = get_container()
        use_case = container.resolve('delete_usuario_use_case')
        
        use_case.execute(usuario_id)
        
        return create_response(message="Usuario desactivado exitosamente")
    except NotFoundError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error al eliminar usuario: {str(e)}",
            status_code=500
        )


@usuario_bp.route('/rol/<string:rol>', methods=['GET'])
@token_required
def get_usuarios_by_rol(current_user, rol):
    """
    Obtener usuarios por rol (solo admin)
    ---
    GET /api/usuarios/rol/:rol (admin o vendedor)
    Response: [{id, nombre, email, rol, ...}]
    """
    try:
        # Solo admin puede filtrar por rol
        if not current_user.get('rol') == 'admin':
            return create_response(
                message="No tienes permisos para esta operación",
                status_code=403
            )
        
        container = get_container()
        use_case = container.resolve('get_usuarios_by_rol_use_case')
        
        usuarios = use_case.execute(rol)
        
        return create_response(data=usuarios)
    except ValidationError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error al obtener usuarios por rol: {str(e)}",
            status_code=500
        )


@usuario_bp.route('/search', methods=['GET'])
@token_required
def search_usuarios(current_user):
    """
    Buscar usuarios por nombre o email (solo admin)
    ---
    GET /api/usuarios/search?q=juan
    Response: [{id, nombre, email, rol, ...}]
    """
    try:
        # Solo admin puede buscar usuarios
        if not current_user.get('rol') == 'admin':
            return create_response(
                message="No tienes permisos para buscar usuarios",
                status_code=403
            )
        
        query = request.args.get('q', '')
        if not query:
            return create_response(
                message="Parámetro de búsqueda 'q' requerido",
                status_code=400
            )
        
        container = get_container()
        use_case = container.resolve('search_usuarios_use_case')
        
        usuarios = use_case.execute(query)
        
        return create_response(data=usuarios)
    except Exception as e:
        return create_response(
            message=f"Error al buscar usuarios: {str(e)}",
            status_code=500
        )


@usuario_bp.route('/<int:usuario_id>/change-password', methods=['PUT'])
@token_required
def change_password(current_user, usuario_id):
    """
    Cambiar contraseña de usuario (el mismo usuario o admin)
    ---
    PUT /api/usuarios/:id/change-password
    Body: {current_password, new_password}
    Response: {message}
    """
    try:
        # Solo el mismo usuario puede cambiar su contraseña
        # (Admin puede resetear con update endpoint)
        if current_user.get('id') != usuario_id:
            return create_response(
                message="Solo puedes cambiar tu propia contraseña",
                status_code=403
            )
        
        data = request.get_json()
        container = get_container()
        use_case = container.resolve('change_password_use_case')
        
        use_case.execute(usuario_id, data)
        
        return create_response(message="Contraseña actualizada exitosamente")
    except ValidationError as e:
        return handle_error(e)
    except NotFoundError as e:
        return handle_error(e)
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error al cambiar contraseña: {str(e)}",
            status_code=500
        )

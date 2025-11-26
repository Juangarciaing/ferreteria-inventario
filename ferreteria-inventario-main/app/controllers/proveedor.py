"""
Controlador de Proveedores (Presentation Layer)
Maneja requests HTTP y delega lógica a Use Cases

Principios aplicados:
- Single Responsibility: Solo maneja HTTP, no lógica de negocio
- Dependency Inversion: Depende de Use Cases (abstracciones), no de implementaciones
- Open/Closed: Abierto a extensión, cerrado a modificación
"""
from flask import Blueprint, request
from app.utils import create_response, handle_error, token_required, rol_requerido
from app.exceptions import BusinessLogicError
from app.application.dtos import ValidationError
from app.infrastructure.di import get_container

proveedor_bp = Blueprint('proveedores', __name__, url_prefix='/api/proveedores')

# Obtener contenedor de DI
container = get_container()


@proveedor_bp.route('', methods=['GET'])
@token_required
def get_proveedores(current_user):
    """
    Obtener todos los proveedores
    
    Query params:
        - solo_activos: bool (opcional) - filtrar solo activos
    """
    try:
        # Resolver caso de uso desde el contenedor
        use_case = container.resolve('get_all_proveedores_use_case')
        
        # Parámetros opcionales
        solo_activos = request.args.get('solo_activos', 'false').lower() == 'true'
        
        # Ejecutar caso de uso
        proveedores = use_case.execute(solo_activos=solo_activos)
        
        # Convertir DTOs a diccionarios para respuesta JSON
        data = [p.to_dict() for p in proveedores]
        
        return create_response(data=data)
        
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error interno del servidor: {str(e)}",
            status_code=500
        )


@proveedor_bp.route('/<int:proveedor_id>', methods=['GET'])
@token_required
def get_proveedor(current_user, proveedor_id):
    """Obtener proveedor por ID"""
    try:
        use_case = container.resolve('get_proveedor_use_case')
        proveedor = use_case.execute(proveedor_id)
        
        return create_response(data=proveedor.to_dict())
        
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error interno del servidor: {str(e)}",
            status_code=500
        )


@proveedor_bp.route('', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_proveedor(current_user):
    """
    Crear nuevo proveedor (solo admin)
    
    Body (JSON):
        - nombre: string (requerido)
        - contacto: string (requerido)
        - telefono: string (opcional)
        - email: string (opcional)
        - direccion: string (opcional)
        - ... (ver CreateProveedorDTO para campos completos)
    """
    try:
        data = request.get_json()
        if not data:
            return create_response(
                message="Body JSON requerido",
                status_code=400
            )
        
        use_case = container.resolve('create_proveedor_use_case')
        proveedor = use_case.execute(data)
        
        return create_response(
            data=proveedor.to_dict(),
            message="Proveedor creado exitosamente",
            status_code=201
        )
        
    except ValidationError as e:
        return create_response(
            message="Errores de validación",
            errors=e.errors,
            status_code=400
        )
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error interno del servidor: {str(e)}",
            status_code=500
        )


@proveedor_bp.route('/<int:proveedor_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_proveedor(current_user, proveedor_id):
    """
    Actualizar proveedor (solo admin)
    Permite actualización parcial de campos
    """
    try:
        data = request.get_json()
        if not data:
            return create_response(
                message="Body JSON requerido",
                status_code=400
            )
        
        use_case = container.resolve('update_proveedor_use_case')
        proveedor = use_case.execute(proveedor_id, data)
        
        return create_response(
            data=proveedor.to_dict(),
            message="Proveedor actualizado exitosamente"
        )
        
    except ValidationError as e:
        return create_response(
            message="Errores de validación",
            errors=e.errors,
            status_code=400
        )
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error interno del servidor: {str(e)}",
            status_code=500
        )


@proveedor_bp.route('/<int:proveedor_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_proveedor(current_user, proveedor_id):
    """Eliminar proveedor (solo admin)"""
    try:
        use_case = container.resolve('delete_proveedor_use_case')
        use_case.execute(proveedor_id)
        
        return create_response(
            message="Proveedor eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error interno del servidor: {str(e)}",
            status_code=500
        )


@proveedor_bp.route('/search', methods=['GET'])
@token_required
def search_proveedores(current_user):
    """
    Buscar proveedores por término
    
    Query params:
        - q: string (requerido) - término de búsqueda
    """
    try:
        term = request.args.get('q', '').strip()
        if not term:
            return create_response(
                message="Parámetro 'q' (término de búsqueda) es requerido",
                status_code=400
            )
        
        use_case = container.resolve('search_proveedores_use_case')
        proveedores = use_case.execute(term)
        
        data = [p.to_dict() for p in proveedores]
        return create_response(data=data)
        
    except ValidationError as e:
        return create_response(
            message="Errores de validación",
            errors=e.errors,
            status_code=400
        )
    except BusinessLogicError as e:
        return handle_error(e)
    except Exception as e:
        return create_response(
            message=f"Error interno del servidor: {str(e)}",
            status_code=500
        )

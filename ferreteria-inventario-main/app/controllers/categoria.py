"""
Controlador de categorías - Clean Architecture
"""
from flask import Blueprint, request
from app.infrastructure.di import get_container
from app.application.dtos.base_dto import ValidationError
from app.exceptions import BusinessLogicError, NotFoundError
from app.utils import create_response, handle_error, token_required, rol_requerido

categoria_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')

# Obtener contenedor de DI
container = get_container()


@categoria_bp.route('', methods=['GET'])
@token_required
def get_categorias(current_user):
    """
    Obtiene todas las categorías
    
    Query Parameters:
        - with_count: bool (opcional) - Incluir conteo de productos
        
    Returns:
        200: Lista de categorías
    """
    try:
        with_count = request.args.get('with_count', 'false').lower() == 'true'
        
        use_case = container.resolve('get_all_categorias_use_case')
        categorias = use_case.execute(with_products_count=with_count)
        
        return create_response(data=[c.to_dict() for c in categorias])
    except Exception as e:
        return handle_error(e)


@categoria_bp.route('/<int:categoria_id>', methods=['GET'])
@token_required
def get_categoria(current_user, categoria_id):
    """
    Obtiene una categoría por ID
    
    Path Parameters:
        - categoria_id: int - ID de la categoría
        
    Returns:
        200: Categoría encontrada
        404: Categoría no encontrada
    """
    try:
        use_case = container.resolve('get_categoria_use_case')
        categoria = use_case.execute(categoria_id)
        
        return create_response(data=categoria.to_dict())
    except NotFoundError as e:
        return create_response(message=str(e), status_code=404)
    except Exception as e:
        return handle_error(e)


@categoria_bp.route('', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_categoria(current_user):
    """
    Crea una nueva categoría
    
    Body:
        - nombre: str (requerido)
        - descripcion: str (opcional)
        
    Returns:
        201: Categoría creada
        400: Datos inválidos
        409: Categoría duplicada
    """
    try:
        data = request.get_json()
        
        use_case = container.resolve('create_categoria_use_case')
        categoria = use_case.execute(data)
        
        return create_response(
            message="Categoría creada exitosamente",
            data=categoria.to_dict(),
            status_code=201
        )
    except ValidationError as e:
        return create_response(
            message="Errores de validación",
            errors=e.errors,
            status_code=400
        )
    except BusinessLogicError as e:
        return create_response(message=str(e), status_code=409)
    except Exception as e:
        return handle_error(e)


@categoria_bp.route('/<int:categoria_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_categoria(current_user, categoria_id):
    """
    Actualiza una categoría existente
    
    Path Parameters:
        - categoria_id: int - ID de la categoría
        
    Body:
        - nombre: str (opcional)
        - descripcion: str (opcional)
        
    Returns:
        200: Categoría actualizada
        400: Datos inválidos
        404: Categoría no encontrada
        409: Categoría duplicada
    """
    try:
        data = request.get_json()
        
        use_case = container.resolve('update_categoria_use_case')
        categoria = use_case.execute(categoria_id, data)
        
        return create_response(
            message="Categoría actualizada exitosamente",
            data=categoria.to_dict()
        )
    except ValidationError as e:
        return create_response(
            message="Errores de validación",
            errors=e.errors,
            status_code=400
        )
    except NotFoundError as e:
        return create_response(message=str(e), status_code=404)
    except BusinessLogicError as e:
        return create_response(message=str(e), status_code=409)
    except Exception as e:
        return handle_error(e)


@categoria_bp.route('/<int:categoria_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_categoria(current_user, categoria_id):
    """
    Elimina una categoría
    
    Path Parameters:
        - categoria_id: int - ID de la categoría
        
    Returns:
        200: Categoría eliminada
        404: Categoría no encontrada
        409: Categoría tiene productos asociados
    """
    try:
        use_case = container.resolve('delete_categoria_use_case')
        use_case.execute(categoria_id)
        
        return create_response(message="Categoría eliminada exitosamente")
    except NotFoundError as e:
        return create_response(message=str(e), status_code=404)
    except BusinessLogicError as e:
        return create_response(message=str(e), status_code=409)
    except Exception as e:
        return handle_error(e)


@categoria_bp.route('/search', methods=['GET'])
@token_required
def search_categorias(current_user):
    """
    Busca categorías por nombre
    
    Query Parameters:
        - q: str - Término de búsqueda (mínimo 2 caracteres)
        
    Returns:
        200: Lista de categorías encontradas
        400: Término inválido
    """
    try:
        term = request.args.get('q', '')
        
        use_case = container.resolve('search_categorias_use_case')
        categorias = use_case.execute(term)
        
        return create_response(data=[c.to_dict() for c in categorias])
    except BusinessLogicError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        return handle_error(e)

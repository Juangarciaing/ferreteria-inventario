"""
Controlador de productos - Clean Architecture
"""
from flask import Blueprint, request
from app.infrastructure.di import get_container
from app.application.dtos.base_dto import ValidationError
from app.exceptions import BusinessLogicError, NotFoundError
from app.utils import create_response, handle_error, token_required, rol_requerido

producto_bp = Blueprint('productos', __name__, url_prefix='/api/productos')

# Obtener contenedor de DI
container = get_container()


# --- PRODUCTOS ---
@producto_bp.route('', methods=['GET'])
@token_required
def get_productos(current_user):
    """
    Obtiene todos los productos con paginación
    
    Query Parameters:
        - categoria_id: int (opcional) - Filtrar por categoría
        - page: int (default: 1) - Número de página
        - per_page: int (default: 20, max: 100) - Items por página
        
    Returns:
        200: {
            "items": [...],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total_items": 150,
                "total_pages": 8,
                "has_prev": false,
                "has_next": true
            }
        }
    """
    try:
        from app.utils.pagination import get_pagination_params, paginate_list
        from app.utils.logger import log_business_operation
        
        # Obtener parámetros de paginación
        page, per_page = get_pagination_params(request)
        categoria_id = request.args.get('categoria_id', type=int)
        
        use_case = container.resolve('get_all_productos_use_case')
        productos = use_case.execute(categoria_id=categoria_id)
        
        # Convertir a dict antes de paginar
        productos_dict = [p.to_dict() for p in productos]
        
        # Aplicar paginación
        paginated = paginate_list(productos_dict, page=page, per_page=per_page)
        
        # Log de la operación
        log_business_operation(
            "READ", 
            "Productos", 
            user=current_user.nombre,
            details=f"Página {page}, {len(paginated.items)} items"
        )
        
        return create_response(data=paginated.to_dict())
    except Exception as e:
        from app.utils.logger import log_error
        log_error(e, context="get_productos", user=current_user.nombre)
        return handle_error(e)


@producto_bp.route('/<int:producto_id>', methods=['GET'])
@token_required
def get_producto(current_user, producto_id):
    """
    Obtiene un producto por ID
    
    Path Parameters:
        - producto_id: int - ID del producto
        
    Returns:
        200: Producto encontrado
        404: Producto no encontrado
    """
    try:
        use_case = container.resolve('get_producto_use_case')
        producto = use_case.execute(producto_id)
        
        return create_response(data=producto.to_dict())
    except NotFoundError as e:
        return create_response(message=str(e), status_code=404)
    except Exception as e:
        return handle_error(e)


@producto_bp.route('', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_producto(current_user):
    """
    Crea un nuevo producto
    
    Body:
        - nombre: str (requerido)
        - precio: float (requerido)
        - stock: int (requerido)
        - categoria_id: int (requerido)
        - stock_minimo: int (opcional, default=5)
        - descripcion: str (opcional)
        - proveedor_id: int (opcional)
        
    Returns:
        201: Producto creado
        400: Datos inválidos
        409: Producto duplicado en la categoría
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return create_response(
                message="No se proporcionaron datos",
                status_code=400
            )
        
        # Validar campos requeridos manualmente antes de pasar al DTO
        required_fields = ['nombre', 'precio', 'stock', 'categoria_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return create_response(
                message="Campos requeridos faltantes",
                errors={'missing_fields': missing_fields},
                status_code=400
            )
        
        # Validar que precio no sea negativo
        if 'precio' in data and (data['precio'] is None or float(data['precio']) < 0):
            return create_response(
                message="El precio debe ser un valor positivo",
                errors={'precio': ['Debe ser mayor o igual a 0']},
                status_code=400
            )
        
        use_case = container.resolve('create_producto_use_case')
        producto = use_case.execute(data)
        
        return create_response(
            message="Producto creado exitosamente",
            data=producto.to_dict(),
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


@producto_bp.route('/<int:producto_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_producto(current_user, producto_id):
    """
    Actualiza un producto existente
    
    Path Parameters:
        - producto_id: int - ID del producto
        
    Body:
        - nombre: str (opcional)
        - precio: float (opcional)
        - stock: int (opcional)
        - categoria_id: int (opcional)
        - stock_minimo: int (opcional)
        - descripcion: str (opcional)
        - proveedor_id: int (opcional)
        
    Returns:
        200: Producto actualizado
        400: Datos inválidos
        404: Producto no encontrado
        409: Producto duplicado
    """
    try:
        data = request.get_json()
        
        use_case = container.resolve('update_producto_use_case')
        producto = use_case.execute(producto_id, data)
        
        return create_response(
            message="Producto actualizado exitosamente",
            data=producto.to_dict()
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


@producto_bp.route('/<int:producto_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_producto(current_user, producto_id):
    """
    Elimina un producto
    
    Path Parameters:
        - producto_id: int - ID del producto
        
    Returns:
        200: Producto eliminado
        404: Producto no encontrado
    """
    try:
        use_case = container.resolve('delete_producto_use_case')
        use_case.execute(producto_id)
        
        return create_response(message="Producto eliminado exitosamente")
    except NotFoundError as e:
        return create_response(message=str(e), status_code=404)
    except Exception as e:
        return handle_error(e)


@producto_bp.route('/search', methods=['GET'])
@token_required
def search_productos(current_user):
    """
    Busca productos por nombre
    
    Query Parameters:
        - q: str - Término de búsqueda (mínimo 2 caracteres)
        
    Returns:
        200: Lista de productos encontrados
        400: Término inválido
    """
    try:
        term = request.args.get('q', '')
        
        use_case = container.resolve('search_productos_use_case')
        productos = use_case.execute(term)
        
        return create_response(data=[p.to_dict() for p in productos])
    except BusinessLogicError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        return handle_error(e)


@producto_bp.route('/stock-bajo', methods=['GET'])
@token_required
def get_stock_bajo(current_user):
    """
    Obtiene productos con stock bajo (stock <= stock_minimo)
    
    Returns:
        200: Lista de productos con stock bajo
    """
    try:
        use_case = container.resolve('get_stock_bajo_use_case')
        productos = use_case.execute()
        
        return create_response(data=[p.to_dict() for p in productos])
    except Exception as e:
        return handle_error(e)


@producto_bp.route('/<int:producto_id>/stock', methods=['PATCH'])
@token_required
@rol_requerido('admin')
def update_stock(current_user, producto_id):
    """
    Actualiza el stock de un producto
    
    Path Parameters:
        - producto_id: int - ID del producto
        
    Body:
        - cantidad: int (requerido) - Cantidad a agregar/restar
        - operacion: str (requerido) - 'add' o 'subtract'
        
    Returns:
        200: Stock actualizado
        400: Datos inválidos
        404: Producto no encontrado
    """
    try:
        data = request.get_json()
        cantidad = data.get('cantidad')
        operacion = data.get('operacion', 'add')
        
        use_case = container.resolve('update_stock_use_case')
        producto = use_case.execute(producto_id, cantidad, operacion)
        
        return create_response(
            message="Stock actualizado exitosamente",
            data=producto.to_dict()
        )
    except NotFoundError as e:
        return create_response(message=str(e), status_code=404)
    except BusinessLogicError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        return handle_error(e)

# Nota: Los endpoints de categorías están en app/controllers/categoria.py
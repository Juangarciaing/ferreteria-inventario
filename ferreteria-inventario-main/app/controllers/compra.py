"""
Controlador de Compra - Clean Architecture
Maneja las peticiones HTTP relacionadas con compras

Principios aplicados:
- Single Responsibility: Solo maneja requests/responses HTTP
- Dependency Inversion: Depende de abstracciones (use cases)
- Open/Closed: Extensible sin modificar el código existente
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.di.container import get_container
from app.exceptions import NotFoundError, ValidationError, BusinessLogicError, DatabaseError
from app.utils import token_required

compra_bp = Blueprint('compras', __name__, url_prefix='/api/compras')


@compra_bp.route('', methods=['POST'])
@token_required
def create_compra(current_user):
    """
    Crea una nueva compra y actualiza el stock del producto
    
    Request Body:
    {
        "producto_id": 1,
        "cantidad": 50,
        "precio_unitario": 8.50,
        "proveedor_id": 1  // Opcional
    }
    
    Returns:
        201: Compra creada exitosamente, stock actualizado
        400: Error de validación
        404: Producto o proveedor no encontrado
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('create_compra_use_case')
        
        data = request.get_json()
        # Usar el usuario autenticado
        data['usuario_id'] = current_user['id']
        
        result = use_case.execute(data)
        
        return jsonify({
            'status': 'success',
            'message': 'Compra registrada exitosamente, stock actualizado',
            'data': result
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'errors': e.errors if hasattr(e, 'errors') else None
        }), 400
    except NotFoundError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al crear compra: {str(e)}'
        }), 500


@compra_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_compra(current_user, id):
    """
    Obtiene una compra por su ID
    
    Args:
        id: ID de la compra
        
    Returns:
        200: Compra encontrada
        404: Compra no encontrada
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_compra_use_case')
        
        result = use_case.execute(id)
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except NotFoundError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener compra: {str(e)}'
        }), 500


@compra_bp.route('', methods=['GET'])
@token_required
def get_all_compras(current_user):
    """
    Obtiene todas las compras con paginación opcional
    
    Query Params:
        limit: Número máximo de compras a devolver (opcional)
        
    Returns:
        200: Lista de compras
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_all_compras_use_case')
        
        limit = request.args.get('limit', type=int)
        
        result = use_case.execute(limit)
        
        return jsonify({
            'status': 'success',
            'data': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener compras: {str(e)}'
        }), 500


@compra_bp.route('/proveedor/<int:proveedor_id>', methods=['GET'])
@token_required
def get_compras_by_proveedor(current_user, proveedor_id):
    """
    Obtiene todas las compras de un proveedor
    
    Args:
        proveedor_id: ID del proveedor
        
    Returns:
        200: Lista de compras del proveedor
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_compras_by_proveedor_use_case')
        
        result = use_case.execute(proveedor_id)
        
        return jsonify({
            'status': 'success',
            'data': result,
            'count': len(result)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener compras por proveedor: {str(e)}'
        }), 500


@compra_bp.route('/producto/<int:producto_id>', methods=['GET'])
@token_required
def get_compras_by_producto(current_user, producto_id):
    """
    Obtiene todas las compras de un producto
    
    Args:
        producto_id: ID del producto
        
    Returns:
        200: Lista de compras del producto
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_compras_by_producto_use_case')
        
        result = use_case.execute(producto_id)
        
        return jsonify({
            'status': 'success',
            'data': result,
            'count': len(result)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener compras por producto: {str(e)}'
        }), 500


@compra_bp.route('/fecha', methods=['GET'])
@token_required
def get_compras_by_date_range(current_user):
    """
    Obtiene compras en un rango de fechas
    
    Query Params:
        fecha_inicio: Fecha de inicio en formato ISO (YYYY-MM-DD)
        fecha_fin: Fecha de fin en formato ISO (YYYY-MM-DD)
        
    Returns:
        200: Lista de compras en el rango
        400: Error de validación (fechas inválidas)
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_compras_by_date_range_use_case')
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'status': 'error',
                'message': 'Se requieren fecha_inicio y fecha_fin'
            }), 400
        
        result = use_case.execute({
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
        
        return jsonify({
            'status': 'success',
            'data': result,
            'count': len(result)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener compras por fecha: {str(e)}'
        }), 500


@compra_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
@token_required
def get_compras_by_usuario(current_user, usuario_id):
    """
    Obtiene todas las compras registradas por un usuario
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        200: Lista de compras del usuario
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_compras_by_usuario_use_case')
        
        result = use_case.execute(usuario_id)
        
        return jsonify({
            'status': 'success',
            'data': result,
            'count': len(result)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener compras por usuario: {str(e)}'
        }), 500


@compra_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_compras_statistics(current_user):
    """
    Obtiene estadísticas de compras
    
    Query Params:
        fecha_inicio: Fecha de inicio (opcional, formato ISO)
        fecha_fin: Fecha de fin (opcional, formato ISO)
        
    Returns:
        200: Estadísticas de compras (total, cantidad, promedio)
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_compras_statistics_use_case')
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        data = {}
        if fecha_inicio:
            data['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            data['fecha_fin'] = fecha_fin
        
        result = use_case.execute(data if data else None)
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500
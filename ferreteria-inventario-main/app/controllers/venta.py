"""
Controlador de Venta - Clean Architecture
Maneja las peticiones HTTP relacionadas con ventas

Principios aplicados:
- Single Responsibility: Solo maneja requests/responses HTTP
- Dependency Inversion: Depende de abstracciones (use cases)
- Open/Closed: Extensible sin modificar el código existente
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.di.container import get_container
from app.exceptions import NotFoundError, ValidationError, BusinessLogicError, DatabaseError
from app.utils import token_required

venta_bp = Blueprint('ventas', __name__, url_prefix='/api/ventas')


@venta_bp.route('', methods=['POST'])
@token_required
def create_venta(current_user):
    """
    Crea una nueva venta con sus detalles
    
    Request Body:
    {
        "usuario_id": 1,
        "detalles": [
            {
                "producto_id": 1,
                "cantidad": 5,
                "precio_unitario": 10.50  // Opcional, se toma del producto
            }
        ],
        "cliente_nombre": "Juan Pérez",  // Opcional
        "cliente_documento": "12345678",  // Opcional
        "cliente_telefono": "555-1234"    // Opcional
    }
    
    Returns:
        201: Venta creada exitosamente con sus detalles
        400: Error de validación (datos inválidos, stock insuficiente)
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('create_venta_use_case')
        
        data = request.get_json()
        # Usar el usuario autenticado
        data['usuario_id'] = current_user['id']
        
        result = use_case.execute(data)
        
        return jsonify({
            'status': 'success',
            'message': 'Venta creada exitosamente',
            'data': result
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'errors': e.errors if hasattr(e, 'errors') else None
        }), 400
    except BusinessLogicError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al crear venta: {str(e)}'
        }), 500


@venta_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_venta(current_user, id):
    """
    Obtiene una venta por su ID con sus detalles
    
    Args:
        id: ID de la venta
        
    Returns:
        200: Venta encontrada con sus detalles
        404: Venta no encontrada
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_venta_use_case')
        
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
            'message': f'Error al obtener venta: {str(e)}'
        }), 500


@venta_bp.route('', methods=['GET'])
@token_required
def get_all_ventas(current_user):
    """
    Obtiene todas las ventas con paginación opcional
    
    Query Params:
        limit: Número máximo de ventas a devolver (opcional)
        
    Returns:
        200: Lista de ventas
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_all_ventas_use_case')
        
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
            'message': f'Error al obtener ventas: {str(e)}'
        }), 500


@venta_bp.route('/fecha', methods=['GET'])
@token_required
def get_ventas_by_date_range(current_user):
    """
    Obtiene ventas en un rango de fechas
    
    Query Params:
        fecha_inicio: Fecha de inicio en formato ISO (YYYY-MM-DD)
        fecha_fin: Fecha de fin en formato ISO (YYYY-MM-DD)
        
    Returns:
        200: Lista de ventas en el rango
        400: Error de validación (fechas inválidas)
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_ventas_by_date_range_use_case')
        
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
            'message': f'Error al obtener ventas por fecha: {str(e)}'
        }), 500


@venta_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
@token_required
def get_ventas_by_usuario(current_user, usuario_id):
    """
    Obtiene todas las ventas de un usuario
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        200: Lista de ventas del usuario
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_ventas_by_usuario_use_case')
        
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
            'message': f'Error al obtener ventas por usuario: {str(e)}'
        }), 500


@venta_bp.route('/cliente/<cliente_documento>', methods=['GET'])
@token_required
def get_ventas_by_cliente(current_user, cliente_documento):
    """
    Obtiene todas las ventas de un cliente
    
    Args:
        cliente_documento: Documento del cliente
        
    Returns:
        200: Lista de ventas del cliente
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_ventas_by_cliente_use_case')
        
        result = use_case.execute(cliente_documento)
        
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
            'message': f'Error al obtener ventas por cliente: {str(e)}'
        }), 500


@venta_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_ventas_statistics(current_user):
    """
    Obtiene estadísticas de ventas
    
    Query Params:
        fecha_inicio: Fecha de inicio (opcional, formato ISO)
        fecha_fin: Fecha de fin (opcional, formato ISO)
        
    Returns:
        200: Estadísticas de ventas (total, cantidad, promedio)
        400: Error de validación
        500: Error del servidor
    """
    try:
        container = get_container()
        use_case = container.resolve('get_ventas_statistics_use_case')
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        data = {}
        if fecha_inicio:
            data['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            data['fecha_fin'] = fecha_fin
        
        result = use_case.execute(data)
        
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
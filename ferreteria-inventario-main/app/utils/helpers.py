"""
Utilidades generales
"""
from flask import jsonify
from app.exceptions import BusinessLogicError

def create_response(data=None, message=None, status_code=200):
    """Crear respuesta JSON estandarizada"""
    response_data = {}
    
    if data is not None:
        response_data['data'] = data
    if message:
        response_data['message'] = message
    
    return jsonify(response_data), status_code

def handle_error(error):
    """Manejador de errores centralizado"""
    if isinstance(error, BusinessLogicError):
        return create_response(message=error.message, status_code=error.status_code)
    
    # Error no controlado
    return create_response(
        message="Error interno del servidor", 
        status_code=500
    )

def paginate_query(query, page=1, per_page=20):
    """Paginación de consultas SQLAlchemy"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
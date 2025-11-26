"""
Excepciones personalizadas para la aplicación
"""

class BusinessLogicError(Exception):
    """Excepción base para errores de lógica de negocio"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ValidationError(BusinessLogicError):
    """Error de validación de datos"""
    def __init__(self, message, field=None):
        super().__init__(message, 400)
        self.field = field

class NotFoundError(BusinessLogicError):
    """Recurso no encontrado"""
    def __init__(self, message="Recurso no encontrado"):
        super().__init__(message, 404)

class UnauthorizedError(BusinessLogicError):
    """Error de autorización"""
    def __init__(self, message="No autorizado"):
        super().__init__(message, 401)

class ForbiddenError(BusinessLogicError):
    """Acceso prohibido"""
    def __init__(self, message="Acceso prohibido"):
        super().__init__(message, 403)

class DatabaseError(BusinessLogicError):
    """Error de base de datos"""
    def __init__(self, message="Error en la base de datos"):
        super().__init__(message, 500)

class StockError(BusinessLogicError):
    """Error relacionado con el stock"""
    def __init__(self, message="Error de stock"):
        super().__init__(message, 400)
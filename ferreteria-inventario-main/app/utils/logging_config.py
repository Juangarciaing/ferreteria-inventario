"""
Configuración del sistema de logging
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """
    Configura el sistema de logging para la aplicación
    
    Args:
        app: Instancia de Flask
    """
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configurar nivel de logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    app.logger.setLevel(getattr(logging, log_level))
    
    # Formato de los logs
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler para errores
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10240000,
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Handler para consola (solo en desarrollo)
    if app.config.get('DEBUG'):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    # Agregar handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    
    app.logger.info('Sistema de logging iniciado')

def log_request(request, response_status):
    """
    Registra información de una petición HTTP
    
    Args:
        request: Objeto request de Flask
        response_status: Código de estado HTTP de la respuesta
    """
    from flask import current_app
    current_app.logger.info(
        f'{request.method} {request.path} - {response_status} - '
        f'IP: {request.remote_addr}'
    )

def log_error(error, context=None):
    """
    Registra un error con contexto adicional
    
    Args:
        error: Excepción o mensaje de error
        context: Dict con contexto adicional (opcional)
    """
    from flask import current_app
    error_msg = str(error)
    
    if context:
        error_msg += f' | Context: {context}'
    
    current_app.logger.error(error_msg, exc_info=True)

def log_audit(user_id, action, table, record_id, details=None):
    """
    Registra una acción de auditoría
    
    Args:
        user_id: ID del usuario que ejecutó la acción
        action: Tipo de acción (CREATE, UPDATE, DELETE, etc.)
        table: Tabla afectada
        record_id: ID del registro afectado
        details: Detalles adicionales (opcional)
    """
    from flask import current_app
    audit_msg = f'AUDIT: User {user_id} - {action} on {table}:{record_id}'
    
    if details:
        audit_msg += f' - {details}'
    
    current_app.logger.info(audit_msg)

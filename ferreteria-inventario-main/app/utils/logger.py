"""
Sistema de Logging Profesional
Registra todas las operaciones, errores y eventos del sistema
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(app):
    """
    Configura el sistema de logging para la aplicación
    
    Crea 3 niveles de logs:
    - app.log: Todos los eventos (INFO, WARNING, ERROR)
    - error.log: Solo errores (ERROR, CRITICAL)
    - access.log: Accesos a endpoints (INFO)
    """
    
    # Crear carpeta de logs si no existe
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configuración del formato de logs
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s (%(funcName)s): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ===== LOG GENERAL (app.log) =====
    # Rotación: 10MB por archivo, mantener 5 backups
    general_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(formatter)
    
    # ===== LOG DE ERRORES (error.log) =====
    error_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'error.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # ===== LOG DE ACCESOS (access.log) =====
    access_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'access.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_formatter = logging.Formatter(
        '[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    access_handler.setFormatter(access_formatter)
    
    # ===== CONFIGURAR APP LOGGER =====
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(general_handler)
    app.logger.addHandler(error_handler)
    
    # Logger separado para accesos
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    
    # Handler para consola (desarrollo)
    if app.config.get('DEBUG', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
    
    app.logger.info('=' * 80)
    app.logger.info(f'Sistema de Ferretería iniciado - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    app.logger.info('=' * 80)
    
    return app.logger


def log_request(request, response_code, user=None):
    """
    Registra un acceso HTTP a un endpoint
    
    Args:
        request: Flask request object
        response_code: Código de respuesta HTTP
        user: Usuario autenticado (opcional)
    """
    access_logger = logging.getLogger('access')
    
    user_info = f"Usuario: {user}" if user else "Usuario: Anónimo"
    
    access_logger.info(
        f"{request.method} {request.path} | "
        f"Status: {response_code} | "
        f"{user_info} | "
        f"IP: {request.remote_addr}"
    )


def log_business_operation(operation, entity, entity_id=None, user=None, details=None):
    """
    Registra una operación de negocio (CRUD)
    
    Args:
        operation: Tipo de operación (CREATE, UPDATE, DELETE, READ)
        entity: Tipo de entidad (Producto, Venta, etc.)
        entity_id: ID de la entidad (opcional)
        user: Usuario que realizó la operación
        details: Detalles adicionales
    """
    logger = logging.getLogger('app')
    
    msg = f"[{operation}] {entity}"
    if entity_id:
        msg += f" #{entity_id}"
    if user:
        msg += f" | Usuario: {user}"
    if details:
        msg += f" | {details}"
    
    logger.info(msg)


def log_error(error, context=None, user=None):
    """
    Registra un error con contexto adicional
    
    Args:
        error: Exception o mensaje de error
        context: Contexto del error (función, endpoint, etc.)
        user: Usuario relacionado (si aplica)
    """
    logger = logging.getLogger('app')
    
    msg = f"ERROR: {str(error)}"
    if context:
        msg += f" | Contexto: {context}"
    if user:
        msg += f" | Usuario: {user}"
    
    logger.error(msg, exc_info=True)

"""
Paquete de utilidades
"""
from .auth import JWTManager, token_required, rol_requerido
from .helpers import create_response, handle_error, paginate_query
from .logger import setup_logger, log_request, log_business_operation, log_error
from .pagination import (
    PaginatedResponse, 
    paginate_query as paginate_db_query,
    paginate_list, 
    get_pagination_params
)

__all__ = [
    'JWTManager',
    'token_required', 
    'rol_requerido',
    'create_response',
    'handle_error',
    'paginate_query',
    'setup_logger',
    'log_request',
    'log_business_operation',
    'log_error',
    'PaginatedResponse',
    'paginate_db_query',
    'paginate_list',
    'get_pagination_params'
]
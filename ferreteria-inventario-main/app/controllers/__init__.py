"""
Paquete de controladores
"""
from .auth import auth_bp
from .producto import producto_bp
from .categoria import categoria_bp
from .venta import venta_bp
# dashboard_bp se movió a api_routes.py (legacy)

__all__ = [
    'auth_bp',
    'producto_bp',
    'categoria_bp',
    'venta_bp'
]
"""
Modelos de la aplicación
"""
from .base import BaseModel
from .usuario import Usuario
from .producto import Categoria, Producto
from .venta import Venta, DetalleVenta
from .compra import Compra
from .proveedor import Proveedor

__all__ = [
    'BaseModel',
    'Usuario',
    'Categoria',
    'Producto',
    'Venta',
    'DetalleVenta',
    'Compra',
    'Proveedor'
]
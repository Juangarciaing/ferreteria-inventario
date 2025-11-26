"""
Domain Layer - Repository Interfaces
Interfaces que definen contratos para repositorios (Inversión de Dependencias)
"""
from .repository_interface import IRepository
from .proveedor_repository_interface import IProveedorRepository
from .producto_repository_interface import IProductoRepository

__all__ = [
    'IRepository',
    'IProveedorRepository', 
    'IProductoRepository'
]

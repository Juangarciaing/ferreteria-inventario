"""
Paquete de repositorios
"""
from .base import BaseRepository
from .proveedor import ProveedorRepository
from .usuario import UsuarioRepository
from .producto import ProductoRepository, CategoriaRepository
from .venta import VentaRepository
from .compra import CompraRepository

__all__ = [
    'BaseRepository',
    'ProveedorRepository',
    'UsuarioRepository',
    'ProductoRepository',
    'CategoriaRepository', 
    'VentaRepository',
    'CompraRepository'
]
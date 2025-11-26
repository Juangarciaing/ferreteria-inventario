"""
Application Layer - DTOs (Data Transfer Objects)
Objetos para transferencia y validación de datos entre capas
"""
from .proveedor_dto import CreateProveedorDTO, UpdateProveedorDTO, ProveedorResponseDTO
from .producto_dto import CreateProductoDTO, UpdateProductoDTO, ProductoResponseDTO
from .base_dto import BaseDTO, ValidationError

__all__ = [
    'BaseDTO',
    'ValidationError',
    'CreateProveedorDTO',
    'UpdateProveedorDTO', 
    'ProveedorResponseDTO',
    'CreateProductoDTO',
    'UpdateProductoDTO',
    'ProductoResponseDTO'
]

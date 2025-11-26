"""
DTOs (Data Transfer Objects) para Compra
Define las estructuras de datos para transferir información de compras

Principios aplicados:
- Single Responsibility: Cada DTO tiene una responsabilidad específica
- Data Validation: Validaciones centralizadas en los DTOs
- Immutability: DTOs como objetos de transferencia inmutables
"""
from dataclasses import dataclass
from typing import Optional, Dict
from decimal import Decimal
from app.application.dtos.base_dto import BaseDTO


@dataclass
class CreateCompraDTO(BaseDTO):
    """
    DTO para crear una nueva compra
    
    Validaciones:
    - producto_id: Debe ser positivo
    - cantidad: Entre 1 y 100,000 unidades
    - precio_unitario: Debe ser positivo (costo)
    - proveedor_id: Opcional pero debe ser positivo si se proporciona
    - usuario_id: Debe ser positivo
    """
    
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    proveedor_id: Optional[int] = None
    usuario_id: Optional[int] = None  # Se asigna desde el token
    
    def validate(self):
        """Validar datos de creación de compra"""
        errors = {}
        
        # Validar producto_id
        if not self.producto_id or self.producto_id <= 0:
            errors['producto_id'] = 'El ID del producto debe ser un número positivo'
        
        # Validar cantidad
        if not self.cantidad or self.cantidad <= 0:
            errors['cantidad'] = 'La cantidad debe ser mayor a 0'
        elif self.cantidad > 100000:
            errors['cantidad'] = 'La cantidad no puede exceder 100,000 unidades'
        
        # Validar precio_unitario
        if not self.precio_unitario or self.precio_unitario <= 0:
            errors['precio_unitario'] = 'El precio unitario debe ser mayor a 0'
        elif self.precio_unitario > 1000000:
            errors['precio_unitario'] = 'El precio unitario no puede exceder 1,000,000'
        
        # Validar proveedor_id (opcional)
        if self.proveedor_id is not None and self.proveedor_id <= 0:
            errors['proveedor_id'] = 'El ID del proveedor debe ser un número positivo'
        
        # Validar usuario_id
        if not self.usuario_id or self.usuario_id <= 0:
            errors['usuario_id'] = 'El ID del usuario debe ser un número positivo'
        
        return errors


@dataclass
class CompraResponseDTO(BaseDTO):
    """
    DTO para la respuesta de una compra
    Incluye información completa de la compra con relaciones
    """
    
    id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: Decimal
    total: Decimal
    proveedor_id: Optional[int]
    proveedor_nombre: Optional[str]
    usuario_id: int
    usuario_nombre: str
    fecha_compra: str
    created_at: str
    
    @staticmethod
    def from_entity(compra) -> 'CompraResponseDTO':
        """
        Crea un DTO desde una entidad Compra
        
        Args:
            compra: Entidad Compra del modelo
            
        Returns:
            CompraResponseDTO con los datos de la compra
        """
        return CompraResponseDTO(
            id=compra.id,
            producto_id=compra.producto_id,
            producto_nombre=compra.producto.nombre if compra.producto else None,
            cantidad=compra.cantidad,
            precio_unitario=compra.precio_unitario,
            total=compra.total,
            proveedor_id=compra.proveedor_id,
            proveedor_nombre=compra.proveedor.nombre if compra.proveedor else None,
            usuario_id=compra.usuario_id,
            usuario_nombre=compra.usuario.nombre if compra.usuario else None,
            fecha_compra=compra.fecha_compra.isoformat() if compra.fecha_compra else None,
            created_at=compra.created_at.isoformat() if compra.created_at else None
        )
    
    def to_dict(self) -> Dict:
        """Convierte el DTO a diccionario"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto_nombre,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'total': float(self.total),
            'proveedor_id': self.proveedor_id,
            'proveedor_nombre': self.proveedor_nombre,
            'usuario_id': self.usuario_id,
            'usuario_nombre': self.usuario_nombre,
            'fecha_compra': self.fecha_compra,
            'created_at': self.created_at
        }


@dataclass
class ComprasSummaryDTO(BaseDTO):
    """
    DTO para resumen/estadísticas de compras
    """
    
    total_compras: Decimal
    cantidad_compras: int
    promedio_compra: Decimal
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convierte el DTO a diccionario"""
        return {
            'total_compras': float(self.total_compras),
            'cantidad_compras': self.cantidad_compras,
            'promedio_compra': float(self.promedio_compra),
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin
        }

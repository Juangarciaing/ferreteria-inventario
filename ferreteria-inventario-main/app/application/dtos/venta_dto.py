"""
Data Transfer Objects para Venta y DetalleVenta
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from decimal import Decimal
from app.application.dtos.base_dto import BaseDTO


@dataclass
class DetalleVentaDTO(BaseDTO):
    """DTO para un detalle de venta (item)"""
    producto_id: int
    cantidad: int
    precio_unitario: Optional[Decimal] = None  # Opcional, se puede obtener del producto
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """
        Valida los datos del detalle de venta
        
        Returns:
            Diccionario con errores de validación por campo
        """
        errors = {}
        
        # Validar producto_id
        self._validate_required(self.producto_id, 'producto_id', errors)
        if self.producto_id and self.producto_id <= 0:
            errors.setdefault('producto_id', []).append('El ID del producto debe ser mayor a 0')
        
        # Validar cantidad
        self._validate_required(self.cantidad, 'cantidad', errors)
        if self.cantidad:
            self._validate_positive(self.cantidad, 'cantidad', errors)
            if self.cantidad > 10000:
                errors.setdefault('cantidad', []).append('La cantidad no puede exceder 10,000 unidades')
        
        # Validar precio_unitario si está presente
        if self.precio_unitario is not None:
            if self.precio_unitario <= 0:
                errors.setdefault('precio_unitario', []).append('El precio debe ser mayor a 0')
        
        return errors
    
    def calculate_subtotal(self, precio: Decimal) -> Decimal:
        """Calcula el subtotal usando el precio proporcionado"""
        return Decimal(self.cantidad) * precio


@dataclass
class CreateVentaDTO(BaseDTO):
    """DTO para crear una venta"""
    usuario_id: int
    detalles: List[Dict[str, Any]]  # Lista de detalles de venta
    cliente_nombre: Optional[str] = None
    cliente_documento: Optional[str] = None
    cliente_telefono: Optional[str] = None
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """
        Valida los datos para crear una venta
        
        Returns:
            Diccionario con errores de validación por campo
        """
        errors = {}
        
        # Validar usuario_id
        self._validate_required(self.usuario_id, 'usuario_id', errors)
        if self.usuario_id and self.usuario_id <= 0:
            errors.setdefault('usuario_id', []).append('El ID del usuario debe ser mayor a 0')
        
        # Validar detalles (debe tener al menos un item)
        self._validate_required(self.detalles, 'detalles', errors)
        if self.detalles:
            if not isinstance(self.detalles, list):
                errors.setdefault('detalles', []).append('Los detalles deben ser una lista')
            elif len(self.detalles) == 0:
                errors.setdefault('detalles', []).append('Debe incluir al menos un producto')
            elif len(self.detalles) > 100:
                errors.setdefault('detalles', []).append('No puede incluir más de 100 productos')
            else:
                # Validar cada detalle
                for i, detalle_data in enumerate(self.detalles):
                    try:
                        detalle = DetalleVentaDTO(**detalle_data)
                        detalle_errors = detalle._get_validation_errors()
                        if detalle_errors:
                            for field, msgs in detalle_errors.items():
                                key = f'detalles[{i}].{field}'
                                errors.setdefault(key, []).extend(msgs)
                    except TypeError as e:
                        errors.setdefault('detalles', []).append(
                            f'Detalle {i}: formato inválido - {str(e)}'
                        )
        
        # Validar información del cliente (opcional pero con formato)
        if self.cliente_nombre:
            self._validate_min_length(self.cliente_nombre, 2, 'cliente_nombre', errors)
            self._validate_max_length(self.cliente_nombre, 200, 'cliente_nombre', errors)
        
        if self.cliente_documento:
            self._validate_min_length(self.cliente_documento, 5, 'cliente_documento', errors)
            self._validate_max_length(self.cliente_documento, 50, 'cliente_documento', errors)
        
        if self.cliente_telefono:
            self._validate_max_length(self.cliente_telefono, 20, 'cliente_telefono', errors)
        
        return errors
    
    def get_detalles_dtos(self) -> List[DetalleVentaDTO]:
        """Convierte la lista de detalles en objetos DetalleVentaDTO"""
        return [DetalleVentaDTO(**detalle_data) for detalle_data in self.detalles]


@dataclass
class DetalleVentaResponseDTO(BaseDTO):
    """DTO de respuesta para un detalle de venta"""
    id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    
    @staticmethod
    def from_entity(detalle) -> 'DetalleVentaResponseDTO':
        """Crea un DTO desde una entidad DetalleVenta"""
        return DetalleVentaResponseDTO(
            id=detalle.id,
            producto_id=detalle.producto_id,
            producto_nombre=detalle.producto.nombre if detalle.producto else "Desconocido",
            cantidad=detalle.cantidad,
            precio_unitario=float(detalle.precio_unitario),
            subtotal=float(detalle.subtotal)
        )
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        return {}


@dataclass
class VentaResponseDTO(BaseDTO):
    """DTO de respuesta para venta"""
    id: int
    fecha: str
    total: float
    usuario_id: int
    usuario_nombre: Optional[str]
    cliente_nombre: Optional[str]
    cliente_documento: Optional[str]
    cliente_telefono: Optional[str]
    detalles: List[Dict[str, Any]]
    created_at: Optional[str]
    
    @staticmethod
    def from_entity(venta) -> 'VentaResponseDTO':
        """
        Crea un DTO de respuesta desde una entidad Venta
        
        Args:
            venta: Entidad Venta del modelo
            
        Returns:
            VentaResponseDTO con los datos de la entidad
        """
        detalles = []
        if hasattr(venta, 'detalles') and venta.detalles:
            detalles = [DetalleVentaResponseDTO.from_entity(d).to_dict() for d in venta.detalles]
        
        usuario_nombre = None
        if hasattr(venta, 'usuario') and venta.usuario:
            usuario_nombre = venta.usuario.nombre
        
        return VentaResponseDTO(
            id=venta.id,
            fecha=venta.fecha.isoformat() if venta.fecha else None,
            total=float(venta.total),
            usuario_id=venta.usuario_id,
            usuario_nombre=usuario_nombre,
            cliente_nombre=venta.cliente_nombre,
            cliente_documento=venta.cliente_documento,
            cliente_telefono=venta.cliente_telefono,
            detalles=detalles,
            created_at=venta.created_at.isoformat() if venta.created_at else None
        )
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """Los DTOs de respuesta no necesitan validación"""
        return {}


@dataclass
class VentasSummaryDTO(BaseDTO):
    """DTO para resumen de ventas"""
    total_ventas: float
    cantidad_ventas: int
    promedio_venta: float
    fecha_inicio: Optional[str]
    fecha_fin: Optional[str]
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        return {}

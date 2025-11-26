"""
DTOs para Producto
Objetos de transferencia de datos con validaciones
"""
from dataclasses import dataclass
from typing import Optional, Dict, List
from .base_dto import BaseDTO

@dataclass
class CreateProductoDTO(BaseDTO):
    """DTO para creación de producto"""
    nombre: str
    categoria_id: int
    precio: float
    stock: int = 0
    stock_minimo: int = 5
    descripcion: Optional[str] = None
    codigo_barra: Optional[str] = None
    marca: Optional[str] = None
    unidad_medida: Optional[str] = None
    ubicacion: Optional[str] = None
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        errors: Dict[str, List[str]] = {}
        
        # Campos requeridos
        self._validate_required(self.nombre, 'nombre', errors)
        self._validate_required(self.categoria_id, 'categoria_id', errors)
        self._validate_required(self.precio, 'precio', errors)
        
        # Validar longitudes
        if self.nombre:
            self._validate_min_length(self.nombre, 2, 'nombre', errors)
            self._validate_max_length(self.nombre, 200, 'nombre', errors)
        
        # Validar números positivos
        if self.precio is not None:
            self._validate_positive(self.precio, 'precio', errors)
        
        if self.stock is not None:
            self._validate_positive(self.stock, 'stock', errors)
        
        if self.stock_minimo is not None:
            self._validate_positive(self.stock_minimo, 'stock_minimo', errors)
        
        return errors


@dataclass
class UpdateProductoDTO(BaseDTO):
    """DTO para actualización de producto"""
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    descripcion: Optional[str] = None
    codigo_barra: Optional[str] = None
    marca: Optional[str] = None
    unidad_medida: Optional[str] = None
    ubicacion: Optional[str] = None
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        errors: Dict[str, List[str]] = {}
        
        # Validar solo campos proporcionados
        if self.nombre is not None:
            self._validate_min_length(self.nombre, 2, 'nombre', errors)
            self._validate_max_length(self.nombre, 200, 'nombre', errors)
        
        if self.precio is not None:
            self._validate_positive(self.precio, 'precio', errors)
        
        if self.stock is not None:
            self._validate_positive(self.stock, 'stock', errors)
        
        if self.stock_minimo is not None:
            self._validate_positive(self.stock_minimo, 'stock_minimo', errors)
        
        return errors


@dataclass
class ProductoResponseDTO(BaseDTO):
    """DTO para respuestas de producto"""
    id: int
    nombre: str
    categoria_id: int
    precio: float
    stock: int
    stock_minimo: int
    descripcion: Optional[str] = None
    codigo_barra: Optional[str] = None
    marca: Optional[str] = None
    unidad_medida: Optional[str] = None
    ubicacion: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: any) -> 'ProductoResponseDTO':
        """Crea DTO desde entidad"""
        if hasattr(entity, 'to_dict'):
            data = entity.to_dict()
        else:
            data = entity.__dict__
            
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

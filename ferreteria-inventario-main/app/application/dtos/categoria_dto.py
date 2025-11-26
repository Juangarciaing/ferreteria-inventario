"""
Data Transfer Objects para Categoría
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from app.application.dtos.base_dto import BaseDTO


@dataclass
class CreateCategoriaDTO(BaseDTO):
    """DTO para crear una categoría"""
    nombre: str
    descripcion: Optional[str] = None
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """
        Valida los datos para crear una categoría
        
        Returns:
            Diccionario con errores de validación por campo
        """
        errors = {}
        
        # Validar nombre requerido
        self._validate_required(self.nombre, 'nombre', errors)
        
        if self.nombre:
            self._validate_min_length(self.nombre, 2, 'nombre', errors)
            self._validate_max_length(self.nombre, 100, 'nombre', errors)
        
        # Descripción es opcional, pero si existe validar longitud
        if self.descripcion:
            self._validate_max_length(self.descripcion, 500, 'descripcion', errors)
        
        return errors


@dataclass
class UpdateCategoriaDTO(BaseDTO):
    """DTO para actualizar una categoría"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """
        Valida los datos para actualizar una categoría
        
        Returns:
            Diccionario con errores de validación por campo
        """
        errors = {}
        
        # Validar nombre si está presente
        if self.nombre is not None:
            self._validate_min_length(self.nombre, 2, 'nombre', errors)
            self._validate_max_length(self.nombre, 100, 'nombre', errors)
        
        # Validar descripción si está presente
        if self.descripcion is not None:
            self._validate_max_length(self.descripcion, 500, 'descripcion', errors)
        
        return errors


@dataclass
class CategoriaResponseDTO(BaseDTO):
    """DTO de respuesta para categoría"""
    id: int
    nombre: str
    descripcion: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    productos_count: Optional[int] = None  # Opcional: número de productos
    
    @staticmethod
    def from_entity(entity) -> 'CategoriaResponseDTO':
        """
        Crea un DTO de respuesta desde una entidad Categoria
        
        Args:
            entity: Entidad Categoria del modelo
            
        Returns:
            CategoriaResponseDTO con los datos de la entidad
        """
        productos_count = None
        if hasattr(entity, 'productos'):
            productos_count = len(entity.productos) if entity.productos else 0
        
        return CategoriaResponseDTO(
            id=entity.id,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            productos_count=productos_count
        )
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """Los DTOs de respuesta no necesitan validación"""
        return {}

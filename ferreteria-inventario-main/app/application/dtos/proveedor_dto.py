"""
DTOs para Proveedor
Objetos de transferencia de datos con validaciones
Principio: Single Responsibility - cada DTO tiene una responsabilidad clara
"""
from dataclasses import dataclass
from typing import Optional, Dict, List
from .base_dto import BaseDTO

@dataclass
class CreateProveedorDTO(BaseDTO):
    """
    DTO para creación de proveedor.
    Valida todos los campos requeridos y formatos.
    """
    nombre: str
    contacto: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None
    sitio_web: Optional[str] = None
    condiciones_pago: Optional[str] = None
    terminos_pago: Optional[str] = None
    tiempo_entrega: Optional[str] = None
    rating: Optional[int] = None
    notas: Optional[str] = None
    estado: str = 'activo'
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """Validaciones específicas para crear proveedor"""
        errors: Dict[str, List[str]] = {}
        
        # Validar campos requeridos
        self._validate_required(self.nombre, 'nombre', errors)
        self._validate_required(self.contacto, 'contacto', errors)
        
        # Validar longitudes
        if self.nombre:
            self._validate_min_length(self.nombre, 2, 'nombre', errors)
            self._validate_max_length(self.nombre, 100, 'nombre', errors)
        
        if self.contacto:
            self._validate_min_length(self.contacto, 2, 'contacto', errors)
            self._validate_max_length(self.contacto, 100, 'contacto', errors)
        
        # Validar email si se proporciona
        if self.email:
            self._validate_email(self.email, 'email', errors)
        
        # Validar rating (1-5)
        if self.rating is not None:
            if not (1 <= self.rating <= 5):
                if 'rating' not in errors:
                    errors['rating'] = []
                errors['rating'].append('rating debe estar entre 1 y 5')
        
        # Validar estado
        valid_estados = ['activo', 'inactivo', 'suspendido']
        if self.estado and self.estado not in valid_estados:
            if 'estado' not in errors:
                errors['estado'] = []
            errors['estado'].append(f'estado debe ser uno de: {", ".join(valid_estados)}')
        
        return errors


@dataclass
class UpdateProveedorDTO(BaseDTO):
    """
    DTO para actualización de proveedor.
    Todos los campos son opcionales (actualización parcial).
    """
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None
    sitio_web: Optional[str] = None
    condiciones_pago: Optional[str] = None
    terminos_pago: Optional[str] = None
    tiempo_entrega: Optional[str] = None
    rating: Optional[int] = None
    notas: Optional[str] = None
    estado: Optional[str] = None
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """Validaciones para actualización (campos opcionales)"""
        errors: Dict[str, List[str]] = {}
        
        # Validar longitudes solo si se proporcionan
        if self.nombre is not None:
            self._validate_min_length(self.nombre, 2, 'nombre', errors)
            self._validate_max_length(self.nombre, 100, 'nombre', errors)
        
        if self.contacto is not None:
            self._validate_min_length(self.contacto, 2, 'contacto', errors)
            self._validate_max_length(self.contacto, 100, 'contacto', errors)
        
        # Validar email si se proporciona
        if self.email:
            self._validate_email(self.email, 'email', errors)
        
        # Validar rating
        if self.rating is not None and not (1 <= self.rating <= 5):
            if 'rating' not in errors:
                errors['rating'] = []
            errors['rating'].append('rating debe estar entre 1 y 5')
        
        # Validar estado
        if self.estado:
            valid_estados = ['activo', 'inactivo', 'suspendido']
            if self.estado not in valid_estados:
                if 'estado' not in errors:
                    errors['estado'] = []
                errors['estado'].append(f'estado debe ser uno de: {", ".join(valid_estados)}')
        
        return errors


@dataclass
class ProveedorResponseDTO(BaseDTO):
    """
    DTO para respuestas de proveedor.
    Representa la estructura de datos que se envía al cliente.
    """
    id: int
    nombre: str
    contacto: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None
    sitio_web: Optional[str] = None
    condiciones_pago: Optional[str] = None
    terminos_pago: Optional[str] = None
    tiempo_entrega: Optional[str] = None
    rating: Optional[int] = None
    notas: Optional[str] = None
    estado: str = 'activo'
    
    @classmethod
    def from_entity(cls, entity: any) -> 'ProveedorResponseDTO':
        """
        Crea DTO desde una entidad de dominio.
        Patrón: Factory Method
        """
        if hasattr(entity, 'to_dict'):
            data = entity.to_dict()
        else:
            data = entity.__dict__
            
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

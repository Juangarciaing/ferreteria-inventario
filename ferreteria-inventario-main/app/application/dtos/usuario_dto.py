"""
DTOs (Data Transfer Objects) para Usuario
Define las estructuras de datos para transferir información de usuarios

Principios aplicados:
- Single Responsibility: Cada DTO tiene una responsabilidad específica
- Data Validation: Validaciones centralizadas en los DTOs
- Security: NO exponer contraseñas en DTOs de respuesta
"""
from dataclasses import dataclass
from typing import Optional, Dict
from app.application.dtos.base_dto import BaseDTO
import re


@dataclass
class CreateUsuarioDTO(BaseDTO):
    """
    DTO para crear un nuevo usuario
    
    Validaciones:
    - nombre: 2-100 caracteres
    - email: Formato válido, único en el sistema
    - password: Mínimo 6 caracteres
    - rol: 'admin' o 'vendedor'
    - telefono: Opcional, máximo 20 caracteres
    - direccion: Opcional, máximo 200 caracteres
    """
    
    nombre: str
    email: str
    password: str
    rol: str = 'vendedor'
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    
    def validate(self):
        """Validar datos de creación de usuario"""
        errors = {}
        
        # Validar nombre
        if not self.nombre or len(self.nombre.strip()) < 2:
            errors['nombre'] = 'El nombre debe tener al menos 2 caracteres'
        elif len(self.nombre) > 100:
            errors['nombre'] = 'El nombre no puede exceder 100 caracteres'
        
        # Validar email
        if not self.email:
            errors['email'] = 'El email es requerido'
        else:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, self.email):
                errors['email'] = 'El formato del email no es válido'
            elif len(self.email) > 100:
                errors['email'] = 'El email no puede exceder 100 caracteres'
        
        # Validar password
        if not self.password:
            errors['password'] = 'La contraseña es requerida'
        elif len(self.password) < 6:
            errors['password'] = 'La contraseña debe tener al menos 6 caracteres'
        elif len(self.password) > 255:
            errors['password'] = 'La contraseña no puede exceder 255 caracteres'
        
        # Validar rol
        if self.rol not in ['admin', 'vendedor']:
            errors['rol'] = 'El rol debe ser "admin" o "vendedor"'
        
        # Validar telefono (opcional)
        if self.telefono and len(self.telefono) > 20:
            errors['telefono'] = 'El teléfono no puede exceder 20 caracteres'
        
        # Validar direccion (opcional)
        if self.direccion and len(self.direccion) > 200:
            errors['direccion'] = 'La dirección no puede exceder 200 caracteres'
        
        return errors


@dataclass
class UpdateUsuarioDTO(BaseDTO):
    """
    DTO para actualizar un usuario existente
    Todos los campos son opcionales excepto validaciones específicas
    """
    
    nombre: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[int] = None
    
    def validate(self):
        """Validar datos de actualización"""
        errors = {}
        
        # Validar nombre si se proporciona
        if self.nombre is not None:
            if len(self.nombre.strip()) < 2:
                errors['nombre'] = 'El nombre debe tener al menos 2 caracteres'
            elif len(self.nombre) > 100:
                errors['nombre'] = 'El nombre no puede exceder 100 caracteres'
        
        # Validar email si se proporciona
        if self.email is not None:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, self.email):
                errors['email'] = 'El formato del email no es válido'
            elif len(self.email) > 100:
                errors['email'] = 'El email no puede exceder 100 caracteres'
        
        # Validar rol si se proporciona
        if self.rol is not None and self.rol not in ['admin', 'vendedor']:
            errors['rol'] = 'El rol debe ser "admin" o "vendedor"'
        
        # Validar telefono si se proporciona
        if self.telefono is not None and len(self.telefono) > 20:
            errors['telefono'] = 'El teléfono no puede exceder 20 caracteres'
        
        # Validar direccion si se proporciona
        if self.direccion is not None and len(self.direccion) > 200:
            errors['direccion'] = 'La dirección no puede exceder 200 caracteres'
        
        # Validar activo si se proporciona
        if self.activo is not None and self.activo not in [0, 1]:
            errors['activo'] = 'El campo activo debe ser 0 o 1'
        
        return errors


@dataclass
class ChangePasswordDTO(BaseDTO):
    """
    DTO para cambiar la contraseña de un usuario
    """
    
    current_password: str
    new_password: str
    
    def validate(self):
        """Validar datos de cambio de contraseña"""
        errors = {}
        
        # Validar contraseña actual
        if not self.current_password:
            errors['current_password'] = 'La contraseña actual es requerida'
        
        # Validar nueva contraseña
        if not self.new_password:
            errors['new_password'] = 'La nueva contraseña es requerida'
        elif len(self.new_password) < 6:
            errors['new_password'] = 'La nueva contraseña debe tener al menos 6 caracteres'
        elif len(self.new_password) > 255:
            errors['new_password'] = 'La nueva contraseña no puede exceder 255 caracteres'
        elif self.current_password == self.new_password:
            errors['new_password'] = 'La nueva contraseña debe ser diferente a la actual'
        
        return errors


@dataclass
class LoginDTO(BaseDTO):
    """
    DTO para autenticación de usuario
    """
    
    email: str
    password: str
    
    def validate(self):
        """Validar datos de login"""
        errors = {}
        
        if not self.email:
            errors['email'] = 'El email es requerido'
        
        if not self.password:
            errors['password'] = 'La contraseña es requerida'
        
        return errors


@dataclass
class UsuarioResponseDTO(BaseDTO):
    """
    DTO para la respuesta de un usuario
    IMPORTANTE: NO incluye el password por seguridad
    """
    
    id: int
    nombre: str
    email: str
    rol: str
    telefono: Optional[str]
    direccion: Optional[str]
    activo: int
    estado: bool  # Campo calculado (activo como boolean)
    created_at: str
    updated_at: Optional[str]
    
    @staticmethod
    def from_entity(usuario) -> 'UsuarioResponseDTO':
        """
        Crea un DTO desde una entidad Usuario
        NO incluye el password
        
        Args:
            usuario: Entidad Usuario del modelo
            
        Returns:
            UsuarioResponseDTO con los datos del usuario (sin password)
        """
        return UsuarioResponseDTO(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            rol=usuario.rol,
            telefono=usuario.telefono,
            direccion=usuario.direccion,
            activo=usuario.activo,
            estado=bool(usuario.activo),
            created_at=usuario.created_at.isoformat() if usuario.created_at else None,
            updated_at=usuario.updated_at.isoformat() if usuario.updated_at else None
        )
    
    def to_dict(self) -> Dict:
        """Convierte el DTO a diccionario (sin password)"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'activo': self.activo,
            'estado': self.estado,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

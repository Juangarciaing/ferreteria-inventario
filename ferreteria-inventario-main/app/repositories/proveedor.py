"""
Repositorio de Proveedor - Implementación concreta
Implementa IProveedorRepository (Infrastructure Layer)

Principios aplicados:
- Dependency Inversion: Implementa interfaz del dominio
- Single Responsibility: Solo maneja persistencia de proveedores
- Interface Segregation: Implementa interfaz específica, no genérica
"""
from typing import List, Optional
from app.models import Proveedor
from app.domain.interfaces import IProveedorRepository
from .base import BaseRepository

class ProveedorRepository(BaseRepository, IProveedorRepository):
    """
    Implementación concreta del repositorio de Proveedor.
    Hereda BaseRepository para CRUD básico e implementa IProveedorRepository.
    """
    model = Proveedor
    
    # Métodos heredados de BaseRepository: get_all, get_by_id, create, update, delete, exists
    
    @classmethod
    def find_by_name(cls, nombre: str) -> Optional[Proveedor]:
        """
        Buscar proveedor por nombre exacto
        Útil para validar duplicados
        """
        return cls.model.query.filter_by(nombre=nombre).first()
    
    @classmethod
    def search_providers(cls, term: str) -> List[Proveedor]:
        """
        Buscar proveedores por término en nombre, contacto o email
        Búsqueda case-insensitive
        """
        search_pattern = f'%{term}%'
        return cls.model.query.filter(
            (cls.model.nombre.ilike(search_pattern)) |
            (cls.model.contacto.ilike(search_pattern)) |
            (cls.model.email.ilike(search_pattern))
        ).all()
    
    @classmethod
    def get_active_providers(cls) -> List[Proveedor]:
        """
        Obtener solo proveedores con estado 'activo'
        Regla de negocio: filtrar por estado
        """
        return cls.model.query.filter_by(estado='activo').all()
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional[Proveedor]:
        """
        Buscar proveedor por email
        Útil para validar emails únicos
        """
        if not email:
            return None
        return cls.model.query.filter_by(email=email).first()

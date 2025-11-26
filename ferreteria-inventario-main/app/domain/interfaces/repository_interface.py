"""
Interfaz base de repositorio (patrón Repository)
Principio: Dependency Inversion (SOLID)
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """
    Interfaz genérica para repositorios.
    Define operaciones CRUD básicas que todos los repositorios deben implementar.
    """
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Obtener todos los registros"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Obtener entidad por ID"""
        pass
    
    @abstractmethod
    def create(self, data: dict) -> T:
        """Crear nueva entidad"""
        pass
    
    @abstractmethod
    def update(self, entity_id: int, data: dict) -> T:
        """Actualizar entidad existente"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Eliminar entidad"""
        pass
    
    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Verificar si existe una entidad"""
        pass

"""
Interfaz de repositorio de Proveedor
Define las operaciones específicas del dominio Proveedor
"""
from abc import abstractmethod
from typing import List, Optional
from .repository_interface import IRepository

class IProveedorRepository(IRepository):
    """
    Interfaz que define operaciones específicas para el repositorio de Proveedores.
    Extiende IRepository con métodos del dominio.
    """
    
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[any]:
        """Buscar proveedor por nombre exacto"""
        pass
    
    @abstractmethod
    def search_providers(self, term: str) -> List[any]:
        """
        Buscar proveedores por término (nombre, contacto, email)
        
        Args:
            term: Término de búsqueda
            
        Returns:
            Lista de proveedores que coinciden con el término
        """
        pass
    
    @abstractmethod
    def get_active_providers(self) -> List[any]:
        """Obtener solo proveedores activos"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[any]:
        """Buscar proveedor por email"""
        pass

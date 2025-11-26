"""
Interfaz del Repositorio de Usuario
Define el contrato para las operaciones de usuario

Principio aplicado:
- Dependency Inversion: Define abstracción independiente de implementación
- Interface Segregation: Solo métodos necesarios para usuarios
"""
from abc import abstractmethod
from typing import List, Optional
from app.domain.interfaces.repository_interface import IRepository


class IUsuarioRepository(IRepository):
    """
    Interfaz que define las operaciones del repositorio de Usuario.
    Hereda de IRepository para operaciones CRUD básicas.
    
    Extiende con operaciones específicas de usuarios:
    - Búsqueda por email
    - Búsqueda por rol
    - Operaciones relacionadas con autenticación
    """
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[any]:
        """
        Obtiene un usuario por su email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    def get_by_rol(self, rol: str) -> List[any]:
        """
        Obtiene todos los usuarios con un rol específico
        
        Args:
            rol: Rol a filtrar ('admin' o 'vendedor')
            
        Returns:
            Lista de usuarios con el rol especificado
        """
        pass
    
    @abstractmethod
    def get_active_users(self) -> List[any]:
        """
        Obtiene todos los usuarios activos
        
        Returns:
            Lista de usuarios activos
        """
        pass
    
    @abstractmethod
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un email ya existe en el sistema
        
        Args:
            email: Email a verificar
            exclude_id: ID de usuario a excluir de la búsqueda (para updates)
            
        Returns:
            True si el email existe, False en caso contrario
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[any]:
        """
        Busca usuarios por nombre o email
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de usuarios que coinciden con la búsqueda
        """
        pass

"""
Repositorio de Usuario - Implementación Clean Architecture
"""
from typing import List, Optional
from app import db
from app.models import Usuario
from app.exceptions import DatabaseError
from app.repositories.base import BaseRepository
from app.domain.interfaces.usuario_repository_interface import IUsuarioRepository


class UsuarioRepository(BaseRepository, IUsuarioRepository):
    """Implementación del repositorio de Usuario"""
    
    model = Usuario
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        try:
            return cls.model.query.filter_by(email=email).first()
        except Exception as e:
            raise DatabaseError(f"Error al buscar usuario por email: {str(e)}")
    
    @classmethod
    def get_by_rol(cls, rol: str) -> List[Usuario]:
        """
        Obtiene todos los usuarios con un rol específico
        
        Args:
            rol: Rol a filtrar ('admin' o 'vendedor')
            
        Returns:
            Lista de usuarios con el rol especificado
        """
        try:
            return cls.model.query.filter_by(rol=rol).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener usuarios por rol: {str(e)}")
    
    @classmethod
    def get_active_users(cls) -> List[Usuario]:
        """
        Obtiene todos los usuarios activos
        
        Returns:
            Lista de usuarios activos
        """
        try:
            return cls.model.query.filter_by(activo=1).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener usuarios activos: {str(e)}")
    
    @classmethod
    def email_exists(cls, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un email ya existe en el sistema
        
        Args:
            email: Email a verificar
            exclude_id: ID de usuario a excluir de la búsqueda (para updates)
            
        Returns:
            True si el email existe, False en caso contrario
        """
        try:
            query = cls.model.query.filter_by(email=email)
            if exclude_id:
                query = query.filter(cls.model.id != exclude_id)
            return query.first() is not None
        except Exception as e:
            raise DatabaseError(f"Error al verificar email: {str(e)}")
    
    @classmethod
    def search(cls, query: str) -> List[Usuario]:
        """
        Busca usuarios por nombre o email
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de usuarios que coinciden con la búsqueda
        """
        try:
            search_pattern = f"%{query}%"
            return cls.model.query.filter(
                db.or_(
                    cls.model.nombre.ilike(search_pattern),
                    cls.model.email.ilike(search_pattern)
                )
            ).all()
        except Exception as e:
            raise DatabaseError(f"Error al buscar usuarios: {str(e)}")
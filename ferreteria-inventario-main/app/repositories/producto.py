"""
Repositorio de Producto - Implementación Clean Architecture
"""
from typing import List, Optional
from app.models import Producto, Categoria
from app.exceptions import DatabaseError
from app.repositories.base import BaseRepository
from app.domain.interfaces.producto_repository_interface import IProductoRepository


class ProductoRepository(BaseRepository, IProductoRepository):
    """Implementación del repositorio de Producto"""
    
    model = Producto
    
    @classmethod
    def find_by_name(cls, nombre: str) -> Optional[Producto]:
        """
        Busca un producto por nombre exacto
        
        Args:
            nombre: Nombre del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        try:
            return cls.model.query.filter_by(nombre=nombre).first()
        except Exception as e:
            raise DatabaseError(f"Error al buscar producto por nombre: {str(e)}")
    
    @classmethod
    def search_products(cls, term: str) -> List[Producto]:
        """
        Busca productos por término (búsqueda parcial en nombre)
        
        Args:
            term: Término de búsqueda
            
        Returns:
            Lista de productos que coinciden con el término
        """
        try:
            return cls.model.query.filter(
                cls.model.nombre.ilike(f'%{term}%')
            ).all()
        except Exception as e:
            raise DatabaseError(f"Error al buscar productos: {str(e)}")
    
    @classmethod
    def get_all_with_categoria(cls) -> List[Producto]:
        """
        Obtiene todos los productos con su categoría (eager loading)
        Optimizado con joinedload para evitar N+1 queries
        
        Returns:
            Lista de productos con categorías precargadas
        """
        from sqlalchemy.orm import joinedload
        from app import db
        
        try:
            return db.session.query(cls.model).options(
                joinedload(cls.model.categoria)
            ).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener productos con categoría: {str(e)}")
    
    @classmethod
    def get_by_categoria(cls, categoria_id: int) -> List[Producto]:
        """
        Obtiene todos los productos de una categoría
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            Lista de productos de la categoría
        """
        try:
            return cls.model.query.filter_by(categoria_id=categoria_id).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener productos por categoría: {str(e)}")
    
    @classmethod
    def get_stock_bajo(cls) -> List[Producto]:
        """
        Obtiene productos con stock menor o igual al stock mínimo
        
        Returns:
            Lista de productos con stock bajo
        """
        try:
            return cls.model.query.filter(
                cls.model.stock <= cls.model.stock_minimo
            ).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener productos con stock bajo: {str(e)}")
    
    @classmethod
    def update_stock(cls, producto_id: int, cantidad: int, operacion: str = 'add') -> Producto:
        """
        Actualiza el stock de un producto
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a agregar o restar
            operacion: 'add' o 'subtract'
            
        Returns:
            Producto con stock actualizado
        """
        try:
            producto = cls.get_by_id(producto_id)
            if not producto:
                raise DatabaseError(f"Producto con ID {producto_id} no encontrado")
            
            if operacion == 'add':
                producto.stock += cantidad
            elif operacion == 'subtract':
                if producto.stock >= cantidad:
                    producto.stock -= cantidad
                else:
                    raise DatabaseError("Stock insuficiente")
            else:
                raise DatabaseError("Operación debe ser 'add' o 'subtract'")
            
            producto.save()
            return producto
        except Exception as e:
            if isinstance(e, DatabaseError):
                raise
            raise DatabaseError(f"Error al actualizar stock: {str(e)}")
    
    @classmethod
    def exists_by_name_and_categoria(cls, nombre: str, categoria_id: int) -> Optional[Producto]:
        """
        Verifica si existe un producto con el mismo nombre en una categoría
        
        Args:
            nombre: Nombre del producto
            categoria_id: ID de la categoría
            
        Returns:
            Producto si existe, None en caso contrario
        """
        try:
            return cls.model.query.filter_by(
                nombre=nombre,
                categoria_id=categoria_id
            ).first()
        except Exception as e:
            raise DatabaseError(f"Error al verificar producto: {str(e)}")


class CategoriaRepository(BaseRepository):
    """
    Repositorio de Categoría - Implementación Clean Architecture
    """
    
    model = Categoria
    
    @classmethod
    def find_by_name(cls, nombre: str) -> Optional[Categoria]:
        """
        Busca una categoría por nombre exacto
        
        Args:
            nombre: Nombre de la categoría
            
        Returns:
            Categoría si existe, None en caso contrario
        """
        try:
            return cls.model.query.filter_by(nombre=nombre).first()
        except Exception as e:
            raise DatabaseError(f"Error al buscar categoría por nombre: {str(e)}")
    
    @classmethod
    def search_categorias(cls, term: str) -> List[Categoria]:
        """
        Busca categorías por término (búsqueda parcial en nombre)
        
        Args:
            term: Término de búsqueda
            
        Returns:
            Lista de categorías que coinciden con el término
        """
        try:
            return cls.model.query.filter(
                cls.model.nombre.ilike(f'%{term}%')
            ).all()
        except Exception as e:
            raise DatabaseError(f"Error al buscar categorías: {str(e)}")
    
    @classmethod
    def get_with_products_count(cls) -> List[Categoria]:
        """
        Obtiene todas las categorías con productos cargados (para conteo)
        
        Returns:
            Lista de categorías con relación productos cargada
        """
        try:
            from sqlalchemy.orm import joinedload
            return cls.model.query.options(joinedload(cls.model.productos)).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener categorías con conteo: {str(e)}")


class CategoriaRepository(BaseRepository):
    """
    Repositorio para operaciones de Categoria
    
    TODO: Migrar a Clean Architecture cuando se implemente el módulo Categoría
    """
    
    model = Categoria
    
    @classmethod
    def find_by_name(cls, nombre: str):
        """Buscar categoría por nombre"""
        try:
            return cls.model.query.filter_by(nombre=nombre).first()
        except Exception as e:
            raise DatabaseError(f"Error al buscar categoría: {str(e)}")
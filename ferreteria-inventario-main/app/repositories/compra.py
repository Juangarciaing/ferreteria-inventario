"""
Repositorio de Compra - Implementación Clean Architecture
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models import Compra
from app.exceptions import DatabaseError
from app.repositories.base import BaseRepository
from app.domain.interfaces.compra_repository_interface import ICompraRepository


class CompraRepository(BaseRepository, ICompraRepository):
    """Implementación del repositorio de Compra"""
    
    model = Compra
    
    @classmethod
    def get_by_proveedor(cls, proveedor_id: int) -> List[Compra]:
        """
        Obtiene todas las compras de un proveedor
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Lista de compras del proveedor
        """
        try:
            return cls.model.query.filter_by(
                proveedor_id=proveedor_id
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener compras por proveedor: {str(e)}")
    
    @classmethod
    def get_by_producto(cls, producto_id: int) -> List[Compra]:
        """
        Obtiene todas las compras de un producto
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Lista de compras del producto
        """
        try:
            return cls.model.query.filter_by(
                producto_id=producto_id
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener compras por producto: {str(e)}")
    
    @classmethod
    def get_by_date_range(cls, fecha_inicio: datetime, fecha_fin: datetime) -> List[Compra]:
        """
        Obtiene compras en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            Lista de compras en el rango especificado
        """
        try:
            return cls.model.query.filter(
                cls.model.created_at >= fecha_inicio,
                cls.model.created_at <= fecha_fin
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener compras por rango de fechas: {str(e)}")
    
    @classmethod
    def get_by_usuario(cls, usuario_id: int) -> List[Compra]:
        """
        Obtiene todas las compras registradas por un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de compras del usuario
        """
        try:
            return cls.model.query.filter_by(
                usuario_id=usuario_id
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener compras por usuario: {str(e)}")
    
    @classmethod
    def get_total_compras(cls, fecha_inicio: Optional[datetime] = None, 
                         fecha_fin: Optional[datetime] = None) -> float:
        """
        Calcula el total de compras en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Total de compras en el rango
        """
        try:
            query = db.session.query(func.sum(cls.model.total))
            
            if fecha_inicio and fecha_fin:
                query = query.filter(
                    cls.model.created_at >= fecha_inicio,
                    cls.model.created_at <= fecha_fin
                )
            elif fecha_inicio:
                query = query.filter(cls.model.created_at >= fecha_inicio)
            elif fecha_fin:
                query = query.filter(cls.model.created_at <= fecha_fin)
            
            result = query.scalar()
            return float(result) if result else 0.0
        except Exception as e:
            raise DatabaseError(f"Error al calcular total de compras: {str(e)}")
    
    @classmethod
    def get_compras_statistics(cls, fecha_inicio: Optional[datetime] = None,
                               fecha_fin: Optional[datetime] = None) -> Dict:
        """
        Obtiene estadísticas de compras
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Diccionario con estadísticas (total, cantidad, promedio)
        """
        try:
            query = db.session.query(
                func.sum(cls.model.total).label('total'),
                func.count(cls.model.id).label('cantidad'),
                func.avg(cls.model.total).label('promedio')
            )
            
            if fecha_inicio and fecha_fin:
                query = query.filter(
                    cls.model.created_at >= fecha_inicio,
                    cls.model.created_at <= fecha_fin
                )
            elif fecha_inicio:
                query = query.filter(cls.model.created_at >= fecha_inicio)
            elif fecha_fin:
                query = query.filter(cls.model.created_at <= fecha_fin)
            
            result = query.one()
            
            return {
                'total': float(result.total) if result.total else 0.0,
                'cantidad': int(result.cantidad) if result.cantidad else 0,
                'promedio': float(result.promedio) if result.promedio else 0.0
            }
        except Exception as e:
            raise DatabaseError(f"Error al obtener estadísticas de compras: {str(e)}")
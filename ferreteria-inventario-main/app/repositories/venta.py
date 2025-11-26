"""
Repositorio de Venta - Implementación Clean Architecture
"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import func
from app import db
from app.models import Venta, DetalleVenta
from app.exceptions import DatabaseError
from app.repositories.base import BaseRepository
from app.domain.interfaces.venta_repository_interface import IVentaRepository


class VentaRepository(BaseRepository, IVentaRepository):
    """Implementación del repositorio de Venta"""
    
    model = Venta
    
    @classmethod
    def get_by_date_range(cls, fecha_inicio: datetime, fecha_fin: datetime) -> List[Venta]:
        """
        Obtiene ventas en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            Lista de ventas en el rango especificado
        """
        try:
            return cls.model.query.filter(
                cls.model.created_at >= fecha_inicio,
                cls.model.created_at <= fecha_fin
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener ventas por rango de fechas: {str(e)}")
    
    @classmethod
    def get_by_usuario(cls, usuario_id: int) -> List[Venta]:
        """
        Obtiene todas las ventas de un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de ventas del usuario
        """
        try:
            return cls.model.query.filter_by(
                usuario_id=usuario_id
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener ventas por usuario: {str(e)}")
    
    @classmethod
    def get_by_cliente(cls, cliente_documento: str) -> List[Venta]:
        """
        Obtiene todas las ventas de un cliente
        
        Args:
            cliente_documento: Documento del cliente
            
        Returns:
            Lista de ventas del cliente
        """
        try:
            return cls.model.query.filter_by(
                cliente_documento=cliente_documento
            ).order_by(cls.model.created_at.desc()).all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener ventas por cliente: {str(e)}")
    
    @classmethod
    def get_total_ventas(cls, fecha_inicio: Optional[datetime] = None, 
                        fecha_fin: Optional[datetime] = None) -> float:
        """
        Calcula el total de ventas en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Total de ventas en el rango
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
            raise DatabaseError(f"Error al calcular total de ventas: {str(e)}")
    
    @classmethod
    def create_with_detalles(cls, venta_data: dict, detalles: List[dict]) -> Venta:
        """
        Crea una venta con sus detalles en una transacción
        
        Args:
            venta_data: Datos de la venta
            detalles: Lista de detalles de la venta
            
        Returns:
            Venta creada con sus detalles
        """
        try:
            # Crear la venta principal
            venta = cls.model(**venta_data)
            db.session.add(venta)
            db.session.flush()  # Para obtener el ID de la venta
            
            # Crear los detalles
            for detalle_data in detalles:
                detalle_data['venta_id'] = venta.id
                detalle = DetalleVenta(**detalle_data)
                db.session.add(detalle)
            
            # Commit de la transacción
            db.session.commit()
            
            # Recargar la venta con sus relaciones
            db.session.refresh(venta)
            return venta
            
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear venta con detalles: {str(e)}")
    
    @classmethod
    def get_ventas_statistics(cls, fecha_inicio: Optional[datetime] = None,
                              fecha_fin: Optional[datetime] = None) -> Dict:
        """
        Obtiene estadísticas de ventas
        
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
            raise DatabaseError(f"Error al obtener estadísticas de ventas: {str(e)}")
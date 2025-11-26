"""
Interfaz del repositorio de Venta
Define el contrato para las operaciones de persistencia de ventas
"""
from abc import abstractmethod
from typing import Optional, List, Tuple
from datetime import datetime
from app.domain.interfaces.repository_interface import IRepository


class IVentaRepository(IRepository):
    """
    Interfaz para el repositorio de Venta
    
    Principio aplicado:
    - Dependency Inversion: Las capas altas dependen de esta abstracción
    - Interface Segregation: Interfaz específica para Venta
    """
    
    @abstractmethod
    def get_by_date_range(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[any]:
        """
        Obtiene ventas en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            Lista de ventas en el rango especificado
        """
        pass
    
    @abstractmethod
    def get_by_usuario(self, usuario_id: int) -> List[any]:
        """
        Obtiene todas las ventas de un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de ventas del usuario
        """
        pass
    
    @abstractmethod
    def get_by_cliente(self, cliente_documento: str) -> List[any]:
        """
        Obtiene todas las ventas de un cliente
        
        Args:
            cliente_documento: Documento del cliente
            
        Returns:
            Lista de ventas del cliente
        """
        pass
    
    @abstractmethod
    def get_total_ventas(self, fecha_inicio: Optional[datetime] = None, 
                        fecha_fin: Optional[datetime] = None) -> float:
        """
        Calcula el total de ventas en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Total de ventas en el rango
        """
        pass
    
    @abstractmethod
    def create_with_detalles(self, venta_data: dict, detalles: List[dict]) -> any:
        """
        Crea una venta con sus detalles en una transacción
        
        Args:
            venta_data: Datos de la venta
            detalles: Lista de detalles de la venta
            
        Returns:
            Venta creada con sus detalles
        """
        pass
    
    @abstractmethod
    def get_ventas_statistics(self, fecha_inicio: Optional[datetime] = None,
                              fecha_fin: Optional[datetime] = None) -> dict:
        """
        Obtiene estadísticas de ventas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Diccionario con estadísticas (total, cantidad, promedio)
        """
        pass

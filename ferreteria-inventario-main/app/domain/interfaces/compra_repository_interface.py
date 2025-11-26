"""
Interfaz del Repositorio de Compra
Define el contrato para las operaciones de compra

Principio aplicado:
- Dependency Inversion: Define abstracción independiente de implementación
- Interface Segregation: Solo métodos necesarios para compras
"""
from abc import abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.interfaces.repository_interface import IRepository


class ICompraRepository(IRepository):
    """
    Interfaz que define las operaciones del repositorio de Compra.
    Hereda de IRepository para operaciones CRUD básicas.
    
    Extiende con operaciones específicas de compras:
    - Búsqueda por proveedor
    - Búsqueda por producto
    - Búsqueda por rango de fechas
    - Estadísticas de compras
    """
    
    @abstractmethod
    def get_by_proveedor(self, proveedor_id: int) -> List[any]:
        """
        Obtiene todas las compras de un proveedor específico
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Lista de compras del proveedor
        """
        pass
    
    @abstractmethod
    def get_by_producto(self, producto_id: int) -> List[any]:
        """
        Obtiene todas las compras de un producto específico
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Lista de compras del producto
        """
        pass
    
    @abstractmethod
    def get_by_date_range(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[any]:
        """
        Obtiene compras en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            Lista de compras en el rango especificado
        """
        pass
    
    @abstractmethod
    def get_by_usuario(self, usuario_id: int) -> List[any]:
        """
        Obtiene todas las compras registradas por un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de compras del usuario
        """
        pass
    
    @abstractmethod
    def get_total_compras(self, fecha_inicio: Optional[datetime] = None, 
                         fecha_fin: Optional[datetime] = None) -> float:
        """
        Calcula el total de compras en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Total de compras en el rango (suma de todos los totales)
        """
        pass
    
    @abstractmethod
    def get_compras_statistics(self, fecha_inicio: Optional[datetime] = None,
                               fecha_fin: Optional[datetime] = None) -> dict:
        """
        Obtiene estadísticas de compras
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            Diccionario con:
            - total: Total en dinero de las compras
            - cantidad: Número de compras realizadas
            - promedio: Promedio por compra
        """
        pass

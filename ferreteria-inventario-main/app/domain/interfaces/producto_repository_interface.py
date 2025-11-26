"""
Interfaz de repositorio de Producto
Define las operaciones específicas del dominio Producto
"""
from abc import abstractmethod
from typing import List, Optional
from .repository_interface import IRepository

class IProductoRepository(IRepository):
    """
    Interfaz que define operaciones específicas para el repositorio de Productos.
    """
    
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[any]:
        """Buscar producto por nombre exacto"""
        pass
    
    @abstractmethod
    def search_products(self, term: str) -> List[any]:
        """Buscar productos por término"""
        pass
    
    @abstractmethod
    def get_by_categoria(self, categoria_id: int) -> List[any]:
        """Obtener productos de una categoría"""
        pass
    
    @abstractmethod
    def get_stock_bajo(self) -> List[any]:
        """
        Obtener productos con stock bajo o agotado.
        Stock bajo: stock <= stock_minimo
        """
        pass
    
    @abstractmethod
    def update_stock(self, producto_id: int, cantidad: int, operacion: str) -> bool:
        """
        Actualizar stock de un producto
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a sumar o restar
            operacion: 'sumar' o 'restar'
        
        Returns:
            True si se actualizó correctamente
        """
        pass
    
    @abstractmethod
    def exists_by_name_and_categoria(self, nombre: str, categoria_id: int, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe producto con nombre y categoría (para evitar duplicados)"""
        pass

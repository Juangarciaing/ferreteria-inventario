"""
Interfaz del repositorio de Categoría
Define el contrato para las operaciones de persistencia de categorías
"""
from abc import abstractmethod
from typing import Optional, List
from app.domain.interfaces.repository_interface import IRepository


class ICategoriaRepository(IRepository):
    """
    Interfaz para el repositorio de Categoría
    
    Principio aplicado:
    - Dependency Inversion: Las capas altas dependen de esta abstracción
    - Interface Segregation: Interfaz específica para Categoría
    """
    
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[any]:
        """
        Busca una categoría por nombre exacto
        
        Args:
            nombre: Nombre de la categoría
            
        Returns:
            Categoría si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    def search_categorias(self, term: str) -> List[any]:
        """
        Busca categorías por término (búsqueda parcial en nombre)
        
        Args:
            term: Término de búsqueda
            
        Returns:
            Lista de categorías que coinciden con el término
        """
        pass
    
    @abstractmethod
    def get_with_products_count(self) -> List[any]:
        """
        Obtiene todas las categorías con el conteo de productos
        
        Returns:
            Lista de categorías con información de cantidad de productos
        """
        pass

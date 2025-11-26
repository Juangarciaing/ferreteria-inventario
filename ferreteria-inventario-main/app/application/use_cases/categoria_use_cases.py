"""
Casos de uso para el módulo de Categorías
"""
from typing import Dict, List
from app.domain.interfaces.categoria_repository_interface import ICategoriaRepository
from app.application.dtos.categoria_dto import (
    CreateCategoriaDTO, UpdateCategoriaDTO, CategoriaResponseDTO
)
from app.exceptions import BusinessLogicError, NotFoundError


class CreateCategoriaUseCase:
    """Caso de uso para crear una categoría"""
    
    def __init__(self, repository: ICategoriaRepository):
        self._repository = repository
    
    def execute(self, data: Dict) -> CategoriaResponseDTO:
        """
        Crea una nueva categoría
        
        Args:
            data: Diccionario con los datos de la categoría
                - nombre: str (requerido)
                - descripcion: str (opcional)
            
        Returns:
            CategoriaResponseDTO con la categoría creada
            
        Raises:
            ValidationError: Si los datos son inválidos
            BusinessLogicError: Si ya existe una categoría con ese nombre
        """
        # 1. Validar datos con DTO
        dto = CreateCategoriaDTO(**data)
        dto.validate()
        
        # 2. Regla de negocio: No permitir categorías duplicadas
        existing = self._repository.find_by_name(dto.nombre)
        if existing:
            raise BusinessLogicError(
                f"Ya existe una categoría con el nombre '{dto.nombre}'",
                {'nombre': dto.nombre}
            )
        
        # 3. Crear categoría en BD
        categoria = self._repository.create(dto.to_dict())
        
        # 4. Retornar DTO de respuesta
        return CategoriaResponseDTO.from_entity(categoria)


class UpdateCategoriaUseCase:
    """Caso de uso para actualizar una categoría"""
    
    def __init__(self, repository: ICategoriaRepository):
        self._repository = repository
    
    def execute(self, id: int, data: Dict) -> CategoriaResponseDTO:
        """
        Actualiza una categoría existente
        
        Args:
            id: ID de la categoría a actualizar
            data: Diccionario con campos a actualizar (todos opcionales)
            
        Returns:
            CategoriaResponseDTO con la categoría actualizada
            
        Raises:
            ValidationError: Si los datos son inválidos
            NotFoundError: Si la categoría no existe
            BusinessLogicError: Si el nuevo nombre duplica otra categoría
        """
        # 1. Validar datos
        dto = UpdateCategoriaDTO(**data)
        dto.validate()
        
        # 2. Verificar que la categoría existe
        categoria = self._repository.get_by_id(id)
        if not categoria:
            raise NotFoundError(f"Categoría con ID {id} no encontrada")
        
        # 3. Verificar duplicados si cambia el nombre
        if dto.nombre and dto.nombre != categoria.nombre:
            existing = self._repository.find_by_name(dto.nombre)
            if existing and existing.id != id:
                raise BusinessLogicError(
                    f"Ya existe otra categoría con el nombre '{dto.nombre}'"
                )
        
        # 4. Actualizar categoría
        updated = self._repository.update(id, dto.to_dict())
        
        # 5. Retornar DTO de respuesta
        return CategoriaResponseDTO.from_entity(updated)


class DeleteCategoriaUseCase:
    """Caso de uso para eliminar una categoría"""
    
    def __init__(self, repository: ICategoriaRepository):
        self._repository = repository
    
    def execute(self, id: int) -> bool:
        """
        Elimina una categoría
        
        Args:
            id: ID de la categoría a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si la categoría no existe
            BusinessLogicError: Si la categoría tiene productos asociados
        """
        # 1. Verificar que existe
        categoria = self._repository.get_by_id(id)
        if not categoria:
            raise NotFoundError(f"Categoría con ID {id} no encontrada")
        
        # 2. Verificar que no tenga productos asociados
        if hasattr(categoria, 'productos') and categoria.productos and len(categoria.productos) > 0:
            raise BusinessLogicError(
                f"No se puede eliminar la categoría '{categoria.nombre}' porque tiene {len(categoria.productos)} producto(s) asociado(s)"
            )
        
        # 3. Eliminar
        return self._repository.delete(id)


class GetCategoriaUseCase:
    """Caso de uso para obtener una categoría por ID"""
    
    def __init__(self, repository: ICategoriaRepository):
        self._repository = repository
    
    def execute(self, id: int) -> CategoriaResponseDTO:
        """
        Obtiene una categoría por su ID
        
        Args:
            id: ID de la categoría
            
        Returns:
            CategoriaResponseDTO con los datos de la categoría
            
        Raises:
            NotFoundError: Si la categoría no existe
        """
        categoria = self._repository.get_by_id(id)
        if not categoria:
            raise NotFoundError(f"Categoría con ID {id} no encontrada")
        
        return CategoriaResponseDTO.from_entity(categoria)


class GetAllCategoriasUseCase:
    """Caso de uso para obtener todas las categorías"""
    
    def __init__(self, repository: ICategoriaRepository):
        self._repository = repository
    
    def execute(self, with_products_count: bool = False) -> List[CategoriaResponseDTO]:
        """
        Obtiene todas las categorías
        
        Args:
            with_products_count: Si True, incluye el conteo de productos por categoría
            
        Returns:
            Lista de CategoriaResponseDTO
        """
        if with_products_count:
            categorias = self._repository.get_with_products_count()
        else:
            categorias = self._repository.get_all()
        
        return [CategoriaResponseDTO.from_entity(c) for c in categorias]


class SearchCategoriasUseCase:
    """Caso de uso para buscar categorías"""
    
    def __init__(self, repository: ICategoriaRepository):
        self._repository = repository
    
    def execute(self, term: str) -> List[CategoriaResponseDTO]:
        """
        Busca categorías por nombre
        
        Args:
            term: Término de búsqueda (mínimo 2 caracteres)
            
        Returns:
            Lista de CategoriaResponseDTO con categorías encontradas
            
        Raises:
            BusinessLogicError: Si el término es muy corto
        """
        if not term or len(term) < 2:
            raise BusinessLogicError(
                "El término de búsqueda debe tener al menos 2 caracteres"
            )
        
        categorias = self._repository.search_categorias(term)
        return [CategoriaResponseDTO.from_entity(c) for c in categorias]

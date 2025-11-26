"""
Casos de uso para el módulo de Productos
"""
from typing import Dict, List
from decimal import Decimal
from app.domain.interfaces.producto_repository_interface import IProductoRepository
from app.application.dtos.producto_dto import (
    CreateProductoDTO, UpdateProductoDTO, ProductoResponseDTO
)
from app.exceptions import BusinessLogicError, NotFoundError


class CreateProductoUseCase:
    """Caso de uso para crear un producto"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, data: Dict) -> ProductoResponseDTO:
        """
        Crea un nuevo producto
        
        Args:
            data: Diccionario con los datos del producto
                - nombre: str (requerido)
                - precio: float/Decimal (requerido)
                - stock: int (requerido)
                - categoria_id: int (requerido)
                - stock_minimo: int (opcional, default=5)
                - descripcion: str (opcional)
                - proveedor_id: int (opcional)
            
        Returns:
            ProductoResponseDTO con el producto creado
            
        Raises:
            ValidationError: Si los datos son inválidos
            BusinessLogicError: Si ya existe un producto con ese nombre en la categoría
        """
        # 1. Validar datos con DTO
        dto = CreateProductoDTO(**data)
        dto.validate()
        
        # 2. Regla de negocio: No permitir productos duplicados en la misma categoría
        existing = self._repository.exists_by_name_and_categoria(
            dto.nombre, 
            dto.categoria_id
        )
        if existing:
            raise BusinessLogicError(
                f"Ya existe un producto '{dto.nombre}' en esta categoría",
                {'nombre': dto.nombre, 'categoria_id': dto.categoria_id}
            )
        
        # 3. Crear producto en BD
        producto_data = dto.to_dict()
        producto = self._repository.create(producto_data)
        
        # 4. Retornar DTO de respuesta
        return ProductoResponseDTO.from_entity(producto)


class UpdateProductoUseCase:
    """Caso de uso para actualizar un producto"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, id: int, data: Dict) -> ProductoResponseDTO:
        """
        Actualiza un producto existente
        
        Args:
            id: ID del producto a actualizar
            data: Diccionario con campos a actualizar (todos opcionales)
            
        Returns:
            ProductoResponseDTO con el producto actualizado
            
        Raises:
            ValidationError: Si los datos son inválidos
            NotFoundError: Si el producto no existe
            BusinessLogicError: Si el nuevo nombre duplica otro producto
        """
        # 1. Validar datos
        dto = UpdateProductoDTO(**data)
        dto.validate()
        
        # 2. Verificar que el producto existe
        producto = self._repository.get_by_id(id)
        if not producto:
            raise NotFoundError(f"Producto con ID {id} no encontrado")
        
        # 3. Verificar duplicados si cambia nombre o categoría
        if dto.nombre or dto.categoria_id:
            new_nombre = dto.nombre if dto.nombre else producto.nombre
            new_categoria_id = dto.categoria_id if dto.categoria_id else producto.categoria_id
            
            # Solo verificar si realmente cambió
            if (new_nombre != producto.nombre or new_categoria_id != producto.categoria_id):
                existing = self._repository.exists_by_name_and_categoria(
                    new_nombre, 
                    new_categoria_id
                )
                if existing and existing.id != id:
                    raise BusinessLogicError(
                        f"Ya existe otro producto '{new_nombre}' en esta categoría"
                    )
        
        # 4. Actualizar producto
        updated = self._repository.update(id, dto.to_dict())
        
        # 5. Retornar DTO de respuesta
        return ProductoResponseDTO.from_entity(updated)


class DeleteProductoUseCase:
    """Caso de uso para eliminar un producto"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, id: int) -> bool:
        """
        Elimina un producto
        
        Args:
            id: ID del producto a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si el producto no existe
        """
        # 1. Verificar que existe
        producto = self._repository.get_by_id(id)
        if not producto:
            raise NotFoundError(f"Producto con ID {id} no encontrado")
        
        # 2. Eliminar
        return self._repository.delete(id)


class GetProductoUseCase:
    """Caso de uso para obtener un producto por ID"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, id: int) -> ProductoResponseDTO:
        """
        Obtiene un producto por su ID
        
        Args:
            id: ID del producto
            
        Returns:
            ProductoResponseDTO con los datos del producto
            
        Raises:
            NotFoundError: Si el producto no existe
        """
        producto = self._repository.get_by_id(id)
        if not producto:
            raise NotFoundError(f"Producto con ID {id} no encontrado")
        
        return ProductoResponseDTO.from_entity(producto)


class GetAllProductosUseCase:
    """Caso de uso para obtener todos los productos"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, categoria_id: int = None) -> List[ProductoResponseDTO]:
        """
        Obtiene todos los productos, opcionalmente filtrados por categoría
        
        Args:
            categoria_id: ID de categoría para filtrar (opcional)
            
        Returns:
            Lista de ProductoResponseDTO
        """
        if categoria_id:
            productos = self._repository.get_by_categoria(categoria_id)
        else:
            productos = self._repository.get_all()
        
        return [ProductoResponseDTO.from_entity(p) for p in productos]


class SearchProductosUseCase:
    """Caso de uso para buscar productos"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, term: str) -> List[ProductoResponseDTO]:
        """
        Busca productos por nombre
        
        Args:
            term: Término de búsqueda (mínimo 2 caracteres)
            
        Returns:
            Lista de ProductoResponseDTO con productos encontrados
            
        Raises:
            BusinessLogicError: Si el término es muy corto
        """
        if not term or len(term) < 2:
            raise BusinessLogicError(
                "El término de búsqueda debe tener al menos 2 caracteres"
            )
        
        productos = self._repository.search_products(term)
        return [ProductoResponseDTO.from_entity(p) for p in productos]


class GetStockBajoUseCase:
    """Caso de uso para obtener productos con stock bajo"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self) -> List[ProductoResponseDTO]:
        """
        Obtiene productos con stock menor o igual al stock mínimo
        
        Returns:
            Lista de ProductoResponseDTO con productos con stock bajo
        """
        productos = self._repository.get_stock_bajo()
        return [ProductoResponseDTO.from_entity(p) for p in productos]


class UpdateStockUseCase:
    """Caso de uso para actualizar el stock de un producto"""
    
    def __init__(self, repository: IProductoRepository):
        self._repository = repository
    
    def execute(self, id: int, cantidad: int, operacion: str = 'add') -> ProductoResponseDTO:
        """
        Actualiza el stock de un producto
        
        Args:
            id: ID del producto
            cantidad: Cantidad a agregar o restar (debe ser positivo)
            operacion: 'add' para agregar, 'subtract' para restar
            
        Returns:
            ProductoResponseDTO con el producto actualizado
            
        Raises:
            NotFoundError: Si el producto no existe
            BusinessLogicError: Si la cantidad es inválida o hay stock insuficiente
        """
        # 1. Validar cantidad
        if cantidad <= 0:
            raise BusinessLogicError("La cantidad debe ser mayor a 0")
        
        # 2. Validar operación
        if operacion not in ['add', 'subtract']:
            raise BusinessLogicError("La operación debe ser 'add' o 'subtract'")
        
        # 3. Verificar que el producto existe
        producto = self._repository.get_by_id(id)
        if not producto:
            raise NotFoundError(f"Producto con ID {id} no encontrado")
        
        # 4. Verificar stock suficiente si es resta
        if operacion == 'subtract' and producto.stock < cantidad:
            raise BusinessLogicError(
                f"Stock insuficiente. Stock actual: {producto.stock}, solicitado: {cantidad}"
            )
        
        # 5. Actualizar stock
        updated = self._repository.update_stock(id, cantidad, operacion)
        
        # 6. Retornar DTO de respuesta
        return ProductoResponseDTO.from_entity(updated)

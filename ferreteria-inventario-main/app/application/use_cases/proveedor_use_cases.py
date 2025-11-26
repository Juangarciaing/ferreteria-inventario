"""
Casos de Uso de Proveedor
Encapsulan la lógica de aplicación y orquestan el flujo de datos

Principios aplicados:
- Single Responsibility: Cada caso de uso hace una cosa
- Dependency Inversion: Depende de interfaces, no de implementaciones concretas
- Open/Closed: Abierto a extensión, cerrado a modificación
"""
from typing import List, Dict
from app.domain.interfaces import IProveedorRepository
from app.application.dtos import (
    CreateProveedorDTO, 
    UpdateProveedorDTO, 
    ProveedorResponseDTO,
    ValidationError
)
from app.exceptions import BusinessLogicError

class CreateProveedorUseCase:
    """
    Caso de uso: Crear nuevo proveedor
    Responsabilidad: Validar, verificar duplicados y crear proveedor
    """
    
    def __init__(self, repository: IProveedorRepository):
        """
        Inyección de dependencias por constructor
        
        Args:
            repository: Implementación de IProveedorRepository
        """
        self._repository = repository
    
    def execute(self, data: Dict) -> ProveedorResponseDTO:
        """
        Ejecuta el caso de uso de creación
        
        Args:
            data: Datos del proveedor a crear
            
        Returns:
            ProveedorResponseDTO con los datos del proveedor creado
            
        Raises:
            ValidationError: Si los datos no son válidos
            BusinessLogicError: Si hay un error de lógica de negocio
        """
        # 1. Validar datos con DTO
        dto = CreateProveedorDTO(**data)
        dto.validate()
        
        # 2. Regla de negocio: Verificar que no exista proveedor con mismo nombre
        if self._repository.find_by_name(dto.nombre):
            raise BusinessLogicError(
                f"Ya existe un proveedor con el nombre '{dto.nombre}'"
            )
        
        # 3. Verificar email único si se proporciona
        if dto.email and self._repository.get_by_email(dto.email):
            raise BusinessLogicError(
                f"Ya existe un proveedor con el email '{dto.email}'"
            )
        
        # 4. Crear proveedor
        proveedor = self._repository.create(dto.to_dict())
        
        # 5. Retornar DTO de respuesta
        return ProveedorResponseDTO.from_entity(proveedor)


class UpdateProveedorUseCase:
    """
    Caso de uso: Actualizar proveedor existente
    """
    
    def __init__(self, repository: IProveedorRepository):
        self._repository = repository
    
    def execute(self, proveedor_id: int, data: Dict) -> ProveedorResponseDTO:
        """
        Actualiza un proveedor
        
        Args:
            proveedor_id: ID del proveedor a actualizar
            data: Datos a actualizar
            
        Returns:
            ProveedorResponseDTO actualizado
        """
        # 1. Validar datos
        dto = UpdateProveedorDTO(**data)
        dto.validate()
        
        # 2. Verificar que existe el proveedor
        proveedor_actual = self._repository.get_by_id(proveedor_id)
        if not proveedor_actual:
            raise BusinessLogicError(f"Proveedor con ID {proveedor_id} no encontrado")
        
        # 3. Si cambia el nombre, verificar que no esté duplicado
        if dto.nombre and dto.nombre != proveedor_actual.nombre:
            existing = self._repository.find_by_name(dto.nombre)
            if existing and existing.id != proveedor_id:
                raise BusinessLogicError(
                    f"Ya existe otro proveedor con el nombre '{dto.nombre}'"
                )
        
        # 4. Si cambia el email, verificar que no esté duplicado
        if dto.email and dto.email != getattr(proveedor_actual, 'email', None):
            existing = self._repository.get_by_email(dto.email)
            if existing and existing.id != proveedor_id:
                raise BusinessLogicError(
                    f"Ya existe otro proveedor con el email '{dto.email}'"
                )
        
        # 5. Actualizar
        proveedor_actualizado = self._repository.update(proveedor_id, dto.to_dict())
        
        return ProveedorResponseDTO.from_entity(proveedor_actualizado)


class DeleteProveedorUseCase:
    """
    Caso de uso: Eliminar proveedor
    """
    
    def __init__(self, repository: IProveedorRepository):
        self._repository = repository
    
    def execute(self, proveedor_id: int) -> bool:
        """
        Elimina un proveedor
        
        Args:
            proveedor_id: ID del proveedor a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        # 1. Verificar que existe
        if not self._repository.exists(proveedor_id):
            raise BusinessLogicError(f"Proveedor con ID {proveedor_id} no encontrado")
        
        # 2. TODO: Verificar si tiene compras asociadas (regla de negocio)
        # Por ahora permite eliminar
        
        # 3. Eliminar
        return self._repository.delete(proveedor_id)


class GetProveedorUseCase:
    """
    Caso de uso: Obtener proveedor por ID
    """
    
    def __init__(self, repository: IProveedorRepository):
        self._repository = repository
    
    def execute(self, proveedor_id: int) -> ProveedorResponseDTO:
        """
        Obtiene un proveedor por ID
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            ProveedorResponseDTO
        """
        proveedor = self._repository.get_by_id(proveedor_id)
        if not proveedor:
            raise BusinessLogicError(f"Proveedor con ID {proveedor_id} no encontrado")
        
        return ProveedorResponseDTO.from_entity(proveedor)


class GetAllProveedoresUseCase:
    """
    Caso de uso: Obtener todos los proveedores
    """
    
    def __init__(self, repository: IProveedorRepository):
        self._repository = repository
    
    def execute(self, solo_activos: bool = False) -> List[ProveedorResponseDTO]:
        """
        Obtiene lista de proveedores
        
        Args:
            solo_activos: Si True, solo retorna proveedores activos
            
        Returns:
            Lista de ProveedorResponseDTO
        """
        if solo_activos:
            proveedores = self._repository.get_active_providers()
        else:
            proveedores = self._repository.get_all()
        
        return [ProveedorResponseDTO.from_entity(p) for p in proveedores]


class SearchProveedoresUseCase:
    """
    Caso de uso: Buscar proveedores por término
    """
    
    def __init__(self, repository: IProveedorRepository):
        self._repository = repository
    
    def execute(self, search_term: str) -> List[ProveedorResponseDTO]:
        """
        Busca proveedores por término
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de ProveedorResponseDTO que coinciden
        """
        if not search_term or not search_term.strip():
            raise ValidationError({'search_term': ['Término de búsqueda requerido']})
        
        proveedores = self._repository.search_providers(search_term.strip())
        return [ProveedorResponseDTO.from_entity(p) for p in proveedores]

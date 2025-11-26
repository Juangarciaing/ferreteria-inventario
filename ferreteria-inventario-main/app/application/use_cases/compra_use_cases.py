"""
Use Cases para Compra
Contienen la lógica de negocio para las operaciones de compras

Principios aplicados:
- Single Responsibility: Cada use case tiene una única responsabilidad
- Dependency Inversion: Dependen de interfaces, no de implementaciones
- Business Logic Isolation: Lógica de negocio separada de infraestructura
"""
from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from app.domain.interfaces.compra_repository_interface import ICompraRepository
from app.domain.interfaces.producto_repository_interface import IProductoRepository
from app.application.dtos.compra_dto import CreateCompraDTO, CompraResponseDTO, ComprasSummaryDTO
from app.exceptions import NotFoundError, ValidationError, BusinessLogicError


class CreateCompraUseCase:
    """
    Caso de uso: Crear una nueva compra
    
    Proceso:
    1. Validar datos de entrada
    2. Verificar que el producto existe
    3. Verificar que el proveedor existe (si se proporcionó)
    4. Calcular el total
    5. Crear la compra
    6. Actualizar stock del producto (SUMAR cantidad)
    7. Retornar DTO de respuesta
    
    Nota: Requiere dos repositorios (Compra + Producto) para coordinar
          la creación de la compra y la actualización del stock
    """
    
    def __init__(self, compra_repository: ICompraRepository, 
                 producto_repository: IProductoRepository):
        self.compra_repository = compra_repository
        self.producto_repository = producto_repository
    
    def execute(self, data: Dict) -> Dict:
        """
        Ejecuta la creación de una compra
        
        Args:
            data: Diccionario con los datos de la compra
            
        Returns:
            Diccionario con los datos de la compra creada
            
        Raises:
            ValidationError: Si los datos son inválidos
            NotFoundError: Si el producto o proveedor no existen
            BusinessLogicError: Si hay un error en la lógica de negocio
        """
        # 1. Validar datos
        dto = CreateCompraDTO(**data)
        errors = dto.validate()
        if errors:
            raise ValidationError("Datos de compra inválidos", errors)
        
        # 2. Verificar que el producto existe
        producto = self.producto_repository.get_by_id(dto.producto_id)
        if not producto:
            raise NotFoundError(f"Producto con ID {dto.producto_id} no encontrado")
        
        # 3. Verificar que el proveedor existe (si se proporcionó)
        if dto.proveedor_id:
            from app.repositories.proveedor import ProveedorRepository
            proveedor = ProveedorRepository.get_by_id(dto.proveedor_id)
            if not proveedor:
                raise NotFoundError(f"Proveedor con ID {dto.proveedor_id} no encontrado")
        
        # 4. Calcular el total
        total = Decimal(dto.cantidad) * Decimal(dto.precio_unitario)
        
        # 5. Preparar datos para crear la compra
        compra_data = {
            'producto_id': dto.producto_id,
            'cantidad': dto.cantidad,
            'precio_unitario': dto.precio_unitario,
            'total': total,
            'proveedor_id': dto.proveedor_id,
            'usuario_id': dto.usuario_id
        }
        
        # 6. Crear la compra
        compra = self.compra_repository.create(**compra_data)
        
        # 7. Actualizar stock del producto (SUMAR)
        nuevo_stock = producto.stock + dto.cantidad
        self.producto_repository.update(dto.producto_id, {'stock': nuevo_stock})
        
        # 8. Retornar DTO de respuesta
        return CompraResponseDTO.from_entity(compra).to_dict()


class GetCompraUseCase:
    """Caso de uso: Obtener una compra por ID"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, compra_id: int) -> Dict:
        """
        Obtiene una compra por su ID
        
        Args:
            compra_id: ID de la compra
            
        Returns:
            Diccionario con los datos de la compra
            
        Raises:
            NotFoundError: Si la compra no existe
        """
        compra = self.compra_repository.get_by_id(compra_id)
        if not compra:
            raise NotFoundError(f"Compra con ID {compra_id} no encontrada")
        
        return CompraResponseDTO.from_entity(compra).to_dict()


class GetAllComprasUseCase:
    """Caso de uso: Obtener todas las compras"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Obtiene todas las compras
        
        Args:
            limit: Límite de resultados (opcional)
            
        Returns:
            Lista de diccionarios con las compras
        """
        compras = self.compra_repository.get_all()
        
        # Aplicar límite si se especificó
        if limit and limit > 0:
            compras = compras[:limit]
        
        return [CompraResponseDTO.from_entity(compra).to_dict() for compra in compras]


class GetComprasByProveedorUseCase:
    """Caso de uso: Obtener compras por proveedor"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, proveedor_id: int) -> List[Dict]:
        """
        Obtiene todas las compras de un proveedor
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Lista de diccionarios con las compras
            
        Raises:
            ValidationError: Si el proveedor_id es inválido
        """
        if not proveedor_id or proveedor_id <= 0:
            raise ValidationError("El ID del proveedor debe ser un número positivo")
        
        compras = self.compra_repository.get_by_proveedor(proveedor_id)
        return [CompraResponseDTO.from_entity(compra).to_dict() for compra in compras]


class GetComprasByProductoUseCase:
    """Caso de uso: Obtener compras por producto"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, producto_id: int) -> List[Dict]:
        """
        Obtiene todas las compras de un producto
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Lista de diccionarios con las compras
            
        Raises:
            ValidationError: Si el producto_id es inválido
        """
        if not producto_id or producto_id <= 0:
            raise ValidationError("El ID del producto debe ser un número positivo")
        
        compras = self.compra_repository.get_by_producto(producto_id)
        return [CompraResponseDTO.from_entity(compra).to_dict() for compra in compras]


class GetComprasByDateRangeUseCase:
    """Caso de uso: Obtener compras por rango de fechas"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, data: Dict) -> List[Dict]:
        """
        Obtiene compras en un rango de fechas
        
        Args:
            data: Diccionario con fecha_inicio y fecha_fin (formato ISO)
            
        Returns:
            Lista de diccionarios con las compras
            
        Raises:
            ValidationError: Si las fechas son inválidas
        """
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        
        if not fecha_inicio_str or not fecha_fin_str:
            raise ValidationError("Se requieren fecha_inicio y fecha_fin")
        
        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
        except ValueError as e:
            raise ValidationError(f"Formato de fecha inválido: {str(e)}")
        
        if fecha_inicio > fecha_fin:
            raise ValidationError("fecha_inicio no puede ser mayor que fecha_fin")
        
        compras = self.compra_repository.get_by_date_range(fecha_inicio, fecha_fin)
        return [CompraResponseDTO.from_entity(compra).to_dict() for compra in compras]


class GetComprasByUsuarioUseCase:
    """Caso de uso: Obtener compras por usuario"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, usuario_id: int) -> List[Dict]:
        """
        Obtiene todas las compras registradas por un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de diccionarios con las compras
            
        Raises:
            ValidationError: Si el usuario_id es inválido
        """
        if not usuario_id or usuario_id <= 0:
            raise ValidationError("El ID del usuario debe ser un número positivo")
        
        compras = self.compra_repository.get_by_usuario(usuario_id)
        return [CompraResponseDTO.from_entity(compra).to_dict() for compra in compras]


class GetComprasStatisticsUseCase:
    """Caso de uso: Obtener estadísticas de compras"""
    
    def __init__(self, compra_repository: ICompraRepository):
        self.compra_repository = compra_repository
    
    def execute(self, data: Optional[Dict] = None) -> Dict:
        """
        Obtiene estadísticas de compras
        
        Args:
            data: Diccionario opcional con fecha_inicio y fecha_fin
            
        Returns:
            Diccionario con estadísticas (total, cantidad, promedio)
            
        Raises:
            ValidationError: Si las fechas son inválidas
        """
        fecha_inicio = None
        fecha_fin = None
        
        if data:
            if 'fecha_inicio' in data:
                try:
                    fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
                except ValueError as e:
                    raise ValidationError(f"Formato de fecha_inicio inválido: {str(e)}")
            
            if 'fecha_fin' in data:
                try:
                    fecha_fin = datetime.fromisoformat(data['fecha_fin'])
                except ValueError as e:
                    raise ValidationError(f"Formato de fecha_fin inválido: {str(e)}")
            
            if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
                raise ValidationError("fecha_inicio no puede ser mayor que fecha_fin")
        
        stats = self.compra_repository.get_compras_statistics(fecha_inicio, fecha_fin)
        
        return ComprasSummaryDTO(
            total_compras=Decimal(str(stats['total'])),
            cantidad_compras=stats['cantidad'],
            promedio_compra=Decimal(str(stats['promedio'])),
            fecha_inicio=fecha_inicio.isoformat() if fecha_inicio else None,
            fecha_fin=fecha_fin.isoformat() if fecha_fin else None
        ).to_dict()

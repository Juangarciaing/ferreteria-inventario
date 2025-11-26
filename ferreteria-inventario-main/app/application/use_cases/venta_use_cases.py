"""
Casos de uso para el módulo de Ventas
"""
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from app.domain.interfaces.venta_repository_interface import IVentaRepository
from app.domain.interfaces.producto_repository_interface import IProductoRepository
from app.application.dtos.venta_dto import (
    CreateVentaDTO, VentaResponseDTO, VentasSummaryDTO, DetalleVentaDTO
)
from app.exceptions import BusinessLogicError, NotFoundError


class CreateVentaUseCase:
    """Caso de uso para crear una venta con sus detalles"""
    
    def __init__(self, venta_repository: IVentaRepository, 
                 producto_repository: IProductoRepository):
        self._venta_repo = venta_repository
        self._producto_repo = producto_repository
    
    def execute(self, data: Dict) -> VentaResponseDTO:
        """
        Crea una nueva venta con sus detalles
        
        Proceso:
        1. Validar datos de entrada
        2. Validar existencia de productos
        3. Validar stock disponible
        4. Calcular subtotales y total
        5. Crear venta y detalles en transacción
        6. Actualizar stock de productos
        
        Args:
            data: Diccionario con datos de la venta
                - usuario_id: int
                - detalles: List[Dict] con producto_id, cantidad
                - cliente_nombre: str (opcional)
                - cliente_documento: str (opcional)
                - cliente_telefono: str (opcional)
            
        Returns:
            VentaResponseDTO con la venta creada
            
        Raises:
            ValidationError: Si los datos son inválidos
            NotFoundError: Si un producto no existe
            BusinessLogicError: Si no hay stock suficiente
        """
        # 1. Validar datos con DTO
        dto = CreateVentaDTO(**data)
        dto.validate()
        
        # 2. Obtener DTOs de detalles
        detalles_dtos = dto.get_detalles_dtos()
        
        # 3. Validar productos y stock
        productos_validados = []
        total_venta = Decimal('0.00')
        
        for detalle_dto in detalles_dtos:
            # Verificar que el producto existe
            producto = self._producto_repo.get_by_id(detalle_dto.producto_id)
            if not producto:
                raise NotFoundError(
                    f"Producto con ID {detalle_dto.producto_id} no encontrado"
                )
            
            # Verificar stock disponible
            if producto.stock < detalle_dto.cantidad:
                raise BusinessLogicError(
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible: {producto.stock}, Solicitado: {detalle_dto.cantidad}"
                )
            
            # Usar precio del producto si no se especificó
            precio = detalle_dto.precio_unitario or producto.precio
            subtotal = detalle_dto.calculate_subtotal(precio)
            total_venta += subtotal
            
            productos_validados.append({
                'producto': producto,
                'detalle_dto': detalle_dto,
                'precio': precio,
                'subtotal': subtotal
            })
        
        # 4. Preparar datos de la venta
        venta_data = {
            'usuario_id': dto.usuario_id,
            'total': float(total_venta),
            'cliente_nombre': dto.cliente_nombre,
            'cliente_documento': dto.cliente_documento,
            'cliente_telefono': dto.cliente_telefono
        }
        
        # 5. Preparar detalles
        detalles_data = []
        for item in productos_validados:
            detalles_data.append({
                'producto_id': item['detalle_dto'].producto_id,
                'cantidad': item['detalle_dto'].cantidad,
                'precio_unitario': float(item['precio']),
                'subtotal': float(item['subtotal'])
            })
        
        # 6. Crear venta con detalles en transacción
        venta = self._venta_repo.create_with_detalles(venta_data, detalles_data)
        
        # 7. Actualizar stock de productos
        for item in productos_validados:
            self._producto_repo.update_stock(
                item['producto'].id,
                item['detalle_dto'].cantidad,
                'subtract'
            )
        
        # 8. Retornar DTO de respuesta
        return VentaResponseDTO.from_entity(venta)


class GetVentaUseCase:
    """Caso de uso para obtener una venta por ID"""
    
    def __init__(self, repository: IVentaRepository):
        self._repository = repository
    
    def execute(self, id: int) -> VentaResponseDTO:
        """
        Obtiene una venta por su ID
        
        Args:
            id: ID de la venta
            
        Returns:
            VentaResponseDTO con los datos de la venta
            
        Raises:
            NotFoundError: Si la venta no existe
        """
        venta = self._repository.get_by_id(id)
        if not venta:
            raise NotFoundError(f"Venta con ID {id} no encontrada")
        
        return VentaResponseDTO.from_entity(venta)


class GetAllVentasUseCase:
    """Caso de uso para obtener todas las ventas"""
    
    def __init__(self, repository: IVentaRepository):
        self._repository = repository
    
    def execute(self, limit: Optional[int] = None) -> List[VentaResponseDTO]:
        """
        Obtiene todas las ventas
        
        Args:
            limit: Número máximo de ventas a retornar (opcional)
            
        Returns:
            Lista de VentaResponseDTO
        """
        ventas = self._repository.get_all()
        
        # Aplicar límite si se especifica
        if limit and limit > 0:
            ventas = ventas[:limit]
        
        return [VentaResponseDTO.from_entity(v) for v in ventas]


class GetVentasByDateRangeUseCase:
    """Caso de uso para obtener ventas por rango de fechas"""
    
    def __init__(self, repository: IVentaRepository):
        self._repository = repository
    
    def execute(self, fecha_inicio: str, fecha_fin: str) -> List[VentaResponseDTO]:
        """
        Obtiene ventas en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio en formato ISO (YYYY-MM-DD)
            fecha_fin: Fecha de fin en formato ISO (YYYY-MM-DD)
            
        Returns:
            Lista de VentaResponseDTO en el rango
            
        Raises:
            BusinessLogicError: Si las fechas son inválidas
        """
        try:
            inicio = datetime.fromisoformat(fecha_inicio)
            fin = datetime.fromisoformat(fecha_fin)
        except ValueError as e:
            raise BusinessLogicError(
                f"Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}"
            )
        
        if inicio > fin:
            raise BusinessLogicError(
                "La fecha de inicio no puede ser posterior a la fecha de fin"
            )
        
        ventas = self._repository.get_by_date_range(inicio, fin)
        return [VentaResponseDTO.from_entity(v) for v in ventas]


class GetVentasByUsuarioUseCase:
    """Caso de uso para obtener ventas de un usuario"""
    
    def __init__(self, repository: IVentaRepository):
        self._repository = repository
    
    def execute(self, usuario_id: int) -> List[VentaResponseDTO]:
        """
        Obtiene todas las ventas de un usuario
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de VentaResponseDTO del usuario
        """
        if usuario_id <= 0:
            raise BusinessLogicError("El ID del usuario debe ser mayor a 0")
        
        ventas = self._repository.get_by_usuario(usuario_id)
        return [VentaResponseDTO.from_entity(v) for v in ventas]


class GetVentasByClienteUseCase:
    """Caso de uso para obtener ventas de un cliente"""
    
    def __init__(self, repository: IVentaRepository):
        self._repository = repository
    
    def execute(self, cliente_documento: str) -> List[VentaResponseDTO]:
        """
        Obtiene todas las ventas de un cliente
        
        Args:
            cliente_documento: Documento del cliente
            
        Returns:
            Lista de VentaResponseDTO del cliente
        """
        if not cliente_documento or len(cliente_documento) < 5:
            raise BusinessLogicError(
                "El documento del cliente debe tener al menos 5 caracteres"
            )
        
        ventas = self._repository.get_by_cliente(cliente_documento)
        return [VentaResponseDTO.from_entity(v) for v in ventas]


class GetVentasStatisticsUseCase:
    """Caso de uso para obtener estadísticas de ventas"""
    
    def __init__(self, repository: IVentaRepository):
        self._repository = repository
    
    def execute(self, fecha_inicio: Optional[str] = None, 
                fecha_fin: Optional[str] = None) -> VentasSummaryDTO:
        """
        Obtiene estadísticas de ventas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional, formato ISO)
            fecha_fin: Fecha de fin (opcional, formato ISO)
            
        Returns:
            VentasSummaryDTO con estadísticas
        """
        inicio = None
        fin = None
        
        if fecha_inicio:
            try:
                inicio = datetime.fromisoformat(fecha_inicio)
            except ValueError:
                raise BusinessLogicError("Formato de fecha de inicio inválido")
        
        if fecha_fin:
            try:
                fin = datetime.fromisoformat(fecha_fin)
            except ValueError:
                raise BusinessLogicError("Formato de fecha de fin inválido")
        
        if inicio and fin and inicio > fin:
            raise BusinessLogicError(
                "La fecha de inicio no puede ser posterior a la fecha de fin"
            )
        
        stats = self._repository.get_ventas_statistics(inicio, fin)
        
        return VentasSummaryDTO(
            total_ventas=stats.get('total', 0.0),
            cantidad_ventas=stats.get('cantidad', 0),
            promedio_venta=stats.get('promedio', 0.0),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

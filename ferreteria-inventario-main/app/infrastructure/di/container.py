"""
Dependency Injection Container
Centraliza la creación e inyección de dependencias

Principio aplicado:
- Dependency Inversion: Las capas altas no dependen de las bajas, dependen de abstracciones
- Inversion of Control: El framework controla la creación de objetos
"""
from typing import Dict, Type, Any, Callable
from app.domain.interfaces import IProveedorRepository, IProductoRepository
from app.domain.interfaces.venta_repository_interface import IVentaRepository
from app.domain.interfaces.compra_repository_interface import ICompraRepository
from app.domain.interfaces.usuario_repository_interface import IUsuarioRepository
from app.repositories import ProveedorRepository, ProductoRepository
from app.repositories.producto import CategoriaRepository
from app.repositories.venta import VentaRepository
from app.repositories.compra import CompraRepository
from app.repositories.usuario import UsuarioRepository
from app.application.use_cases import (
    CreateProveedorUseCase,
    UpdateProveedorUseCase,
    DeleteProveedorUseCase,
    GetProveedorUseCase,
    GetAllProveedoresUseCase,
    SearchProveedoresUseCase
)
from app.application.use_cases.producto_use_cases import (
    CreateProductoUseCase,
    UpdateProductoUseCase,
    DeleteProductoUseCase,
    GetProductoUseCase,
    GetAllProductosUseCase,
    SearchProductosUseCase,
    GetStockBajoUseCase,
    UpdateStockUseCase
)
from app.application.use_cases.categoria_use_cases import (
    CreateCategoriaUseCase,
    UpdateCategoriaUseCase,
    DeleteCategoriaUseCase,
    GetCategoriaUseCase,
    GetAllCategoriasUseCase,
    SearchCategoriasUseCase
)
from app.application.use_cases.venta_use_cases import (
    CreateVentaUseCase,
    GetVentaUseCase,
    GetAllVentasUseCase,
    GetVentasByDateRangeUseCase,
    GetVentasByUsuarioUseCase,
    GetVentasByClienteUseCase,
    GetVentasStatisticsUseCase
)
from app.application.use_cases.compra_use_cases import (
    CreateCompraUseCase,
    GetCompraUseCase,
    GetAllComprasUseCase,
    GetComprasByProveedorUseCase,
    GetComprasByProductoUseCase,
    GetComprasByDateRangeUseCase,
    GetComprasByUsuarioUseCase,
    GetComprasStatisticsUseCase
)
from app.application.use_cases.usuario_use_cases import (
    CreateUsuarioUseCase,
    UpdateUsuarioUseCase,
    DeleteUsuarioUseCase,
    GetUsuarioUseCase,
    GetAllUsuariosUseCase,
    GetUsuariosByRolUseCase,
    SearchUsuariosUseCase,
    LoginUseCase,
    ChangePasswordUseCase
)

class DIContainer:
    """
    Contenedor de Inyección de Dependencias.
    Registra y resuelve dependencias de forma centralizada.
    
    Patrón: Service Locator + Dependency Injection
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Registra las dependencias por defecto del sistema"""
        
        # Registrar Repositorios (Singleton - una sola instancia)
        self.register_singleton('proveedor_repository', ProveedorRepository)
        self.register_singleton('producto_repository', ProductoRepository)
        self.register_singleton('categoria_repository', CategoriaRepository)
        self.register_singleton('venta_repository', VentaRepository)
        self.register_singleton('compra_repository', CompraRepository)
        self.register_singleton('usuario_repository', UsuarioRepository)
        
        # ===== PROVEEDOR USE CASES =====
        self.register_factory('create_proveedor_use_case', 
                            lambda: CreateProveedorUseCase(self.resolve('proveedor_repository')))
        self.register_factory('update_proveedor_use_case',
                            lambda: UpdateProveedorUseCase(self.resolve('proveedor_repository')))
        self.register_factory('delete_proveedor_use_case',
                            lambda: DeleteProveedorUseCase(self.resolve('proveedor_repository')))
        self.register_factory('get_proveedor_use_case',
                            lambda: GetProveedorUseCase(self.resolve('proveedor_repository')))
        self.register_factory('get_all_proveedores_use_case',
                            lambda: GetAllProveedoresUseCase(self.resolve('proveedor_repository')))
        self.register_factory('search_proveedores_use_case',
                            lambda: SearchProveedoresUseCase(self.resolve('proveedor_repository')))
        
        # ===== PRODUCTO USE CASES =====
        self.register_factory('create_producto_use_case',
                            lambda: CreateProductoUseCase(self.resolve('producto_repository')))
        self.register_factory('update_producto_use_case',
                            lambda: UpdateProductoUseCase(self.resolve('producto_repository')))
        self.register_factory('delete_producto_use_case',
                            lambda: DeleteProductoUseCase(self.resolve('producto_repository')))
        self.register_factory('get_producto_use_case',
                            lambda: GetProductoUseCase(self.resolve('producto_repository')))
        self.register_factory('get_all_productos_use_case',
                            lambda: GetAllProductosUseCase(self.resolve('producto_repository')))
        self.register_factory('search_productos_use_case',
                            lambda: SearchProductosUseCase(self.resolve('producto_repository')))
        self.register_factory('get_stock_bajo_use_case',
                            lambda: GetStockBajoUseCase(self.resolve('producto_repository')))
        self.register_factory('update_stock_use_case',
                            lambda: UpdateStockUseCase(self.resolve('producto_repository')))
        
        # ===== CATEGORÍA USE CASES =====
        self.register_factory('create_categoria_use_case',
                            lambda: CreateCategoriaUseCase(self.resolve('categoria_repository')))
        self.register_factory('update_categoria_use_case',
                            lambda: UpdateCategoriaUseCase(self.resolve('categoria_repository')))
        self.register_factory('delete_categoria_use_case',
                            lambda: DeleteCategoriaUseCase(self.resolve('categoria_repository')))
        self.register_factory('get_categoria_use_case',
                            lambda: GetCategoriaUseCase(self.resolve('categoria_repository')))
        self.register_factory('get_all_categorias_use_case',
                            lambda: GetAllCategoriasUseCase(self.resolve('categoria_repository')))
        self.register_factory('search_categorias_use_case',
                            lambda: SearchCategoriasUseCase(self.resolve('categoria_repository')))
        
        # ===== VENTA USE CASES =====
        # CreateVentaUseCase necesita dos repositorios
        self.register_factory('create_venta_use_case',
                            lambda: CreateVentaUseCase(
                                self.resolve('venta_repository'),
                                self.resolve('producto_repository')
                            ))
        self.register_factory('get_venta_use_case',
                            lambda: GetVentaUseCase(self.resolve('venta_repository')))
        self.register_factory('get_all_ventas_use_case',
                            lambda: GetAllVentasUseCase(self.resolve('venta_repository')))
        self.register_factory('get_ventas_by_date_range_use_case',
                            lambda: GetVentasByDateRangeUseCase(self.resolve('venta_repository')))
        self.register_factory('get_ventas_by_usuario_use_case',
                            lambda: GetVentasByUsuarioUseCase(self.resolve('venta_repository')))
        self.register_factory('get_ventas_by_cliente_use_case',
                            lambda: GetVentasByClienteUseCase(self.resolve('venta_repository')))
        self.register_factory('get_ventas_statistics_use_case',
                            lambda: GetVentasStatisticsUseCase(self.resolve('venta_repository')))
        
        # ===== COMPRA USE CASES =====
        # CreateCompraUseCase necesita dos repositorios (similar a Venta)
        self.register_factory('create_compra_use_case',
                            lambda: CreateCompraUseCase(
                                self.resolve('compra_repository'),
                                self.resolve('producto_repository')
                            ))
        self.register_factory('get_compra_use_case',
                            lambda: GetCompraUseCase(self.resolve('compra_repository')))
        self.register_factory('get_all_compras_use_case',
                            lambda: GetAllComprasUseCase(self.resolve('compra_repository')))
        self.register_factory('get_compras_by_proveedor_use_case',
                            lambda: GetComprasByProveedorUseCase(self.resolve('compra_repository')))
        self.register_factory('get_compras_by_producto_use_case',
                            lambda: GetComprasByProductoUseCase(self.resolve('compra_repository')))
        self.register_factory('get_compras_by_date_range_use_case',
                            lambda: GetComprasByDateRangeUseCase(self.resolve('compra_repository')))
        self.register_factory('get_compras_by_usuario_use_case',
                            lambda: GetComprasByUsuarioUseCase(self.resolve('compra_repository')))
        self.register_factory('get_compras_statistics_use_case',
                            lambda: GetComprasStatisticsUseCase(self.resolve('compra_repository')))
        
        # ===== USUARIO USE CASES =====
        self.register_factory('create_usuario_use_case',
                            lambda: CreateUsuarioUseCase(self.resolve('usuario_repository')))
        self.register_factory('update_usuario_use_case',
                            lambda: UpdateUsuarioUseCase(self.resolve('usuario_repository')))
        self.register_factory('delete_usuario_use_case',
                            lambda: DeleteUsuarioUseCase(self.resolve('usuario_repository')))
        self.register_factory('get_usuario_use_case',
                            lambda: GetUsuarioUseCase(self.resolve('usuario_repository')))
        self.register_factory('get_all_usuarios_use_case',
                            lambda: GetAllUsuariosUseCase(self.resolve('usuario_repository')))
        self.register_factory('get_usuarios_by_rol_use_case',
                            lambda: GetUsuariosByRolUseCase(self.resolve('usuario_repository')))
        self.register_factory('search_usuarios_use_case',
                            lambda: SearchUsuariosUseCase(self.resolve('usuario_repository')))
        self.register_factory('login_use_case',
                            lambda: LoginUseCase(self.resolve('usuario_repository')))
        self.register_factory('change_password_use_case',
                            lambda: ChangePasswordUseCase(self.resolve('usuario_repository')))
    
    def register_singleton(self, name: str, service_class: Type):
        """
        Registra un servicio como singleton (una sola instancia compartida)
        
        Args:
            name: Nombre del servicio
            service_class: Clase del servicio
        """
        self._services[name] = service_class
    
    def register_factory(self, name: str, factory: Callable):
        """
        Registra una factory (crea nueva instancia cada vez)
        
        Args:
            name: Nombre del servicio
            factory: Función que crea el servicio
        """
        self._factories[name] = factory
    
    def resolve(self, name: str) -> Any:
        """
        Resuelve una dependencia registrada
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Instancia del servicio
            
        Raises:
            KeyError: Si el servicio no está registrado
        """
        # Si es una factory, ejecutarla
        if name in self._factories:
            return self._factories[name]()
        
        # Si es un singleton, devolverlo
        if name in self._services:
            return self._services[name]
        
        raise KeyError(f"Servicio '{name}' no está registrado en el contenedor DI")
    
    def register_custom(self, name: str, instance: Any):
        """
        Registra una instancia personalizada
        
        Args:
            name: Nombre del servicio
            instance: Instancia del servicio
        """
        self._services[name] = instance


# Instancia global del contenedor (Singleton)
container = DIContainer()


def get_container() -> DIContainer:
    """
    Obtiene la instancia del contenedor de DI
    
    Returns:
        DIContainer global
    """
    return container

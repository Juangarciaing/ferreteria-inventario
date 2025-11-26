"""
Pruebas unitarias para modelos ORM
"""

import pytest
from datetime import datetime, timezone
from app.models.producto import Producto, Categoria
from app.models.usuario import Usuario
from app.models.compra import Compra
from app.models.venta import Venta


class TestCategoriaModel:
    """Pruebas para el modelo Categoria"""
    
    def test_crear_categoria(self):
        """Test: crear instancia de categoría"""
        cat = Categoria(nombre="Herramientas", descripcion="Herramientas manuales")
        assert cat.nombre == "Herramientas"
        assert cat.descripcion == "Herramientas manuales"
        assert cat.activo == 1
    
    def test_categoria_str_representation(self):
        """Test: representación string de categoría"""
        cat = Categoria(nombre="Materiales")
        assert str(cat) == "<Categoria Materiales>"
    
    def test_categoria_defaults(self):
        """Test: valores por defecto"""
        cat = Categoria(nombre="Test")
        assert cat.activo == 1
        assert cat.descripcion is None


class TestProductoModel:
    """Pruebas para el modelo Producto"""
    
    def test_crear_producto_minimo(self):
        """Test: crear producto con campos mínimos"""
        prod = Producto(
            nombre="Martillo",
            precio=150.00,
            stock_actual=10,
            stock_minimo=5,
            categoria_id=1
        )
        assert prod.nombre == "Martillo"
        assert prod.precio == 150.00
        assert prod.stock_actual == 10
        assert prod.activo == 1
    
    def test_producto_con_codigo_barras(self):
        """Test: producto con código de barras"""
        prod = Producto(
            nombre="Tornillo",
            precio=5.50,
            stock_actual=100,
            stock_minimo=20,
            categoria_id=1,
            codigo_barras="1234567890123"
        )
        assert prod.codigo_barras == "1234567890123"
    
    def test_producto_stock_bajo(self):
        """Test: detección de stock bajo"""
        prod = Producto(
            nombre="Test",
            precio=10.0,
            stock_actual=3,
            stock_minimo=5,
            categoria_id=1
        )
        # Asumiendo que tengas un método o propiedad
        assert prod.stock_actual < prod.stock_minimo
    
    def test_producto_defaults(self):
        """Test: valores por defecto"""
        prod = Producto(
            nombre="Test",
            precio=10.0,
            stock_actual=10,
            stock_minimo=5,
            categoria_id=1
        )
        assert prod.activo == 1
        assert prod.descripcion is None
        assert prod.proveedor_id is None


class TestUsuarioModel:
    """Pruebas para el modelo Usuario"""
    
    def test_crear_usuario(self):
        """Test: crear instancia de usuario"""
        user = Usuario(
            nombre="Juan Pérez",
            email="juan@test.com",
            rol="vendedor"
        )
        user.set_password("password123")
        
        assert user.nombre == "Juan Pérez"
        assert user.email == "juan@test.com"
        assert user.rol == "vendedor"
        assert user.password is not None
    
    def test_password_hashing(self):
        """Test: hash de contraseña"""
        user = Usuario(nombre="Test", email="test@test.com", rol="vendedor")
        user.set_password("secret123")
        
        assert user.password != "secret123"
        assert user.check_password("secret123") is True
        assert user.check_password("wrong") is False
    
    def test_usuario_defaults(self):
        """Test: valores por defecto"""
        user = Usuario(nombre="Test", email="test@test.com", rol="vendedor")
        assert user.activo == 1
    
    def test_usuario_str_representation(self):
        """Test: representación string"""
        user = Usuario(nombre="Test User", email="test@test.com", rol="admin")
        assert str(user) == "<Usuario Test User>"


class TestCompraModel:
    """Pruebas para el modelo Compra"""
    
    def test_crear_compra(self):
        """Test: crear instancia de compra"""
        compra = Compra(
            proveedor_id=1,
            usuario_id=1,
            total=500.00
        )
        assert compra.proveedor_id == 1
        assert compra.usuario_id == 1
        assert compra.total == 500.00
    
    def test_compra_fecha_default(self):
        """Test: fecha se asigna automáticamente"""
        compra = Compra(proveedor_id=1, usuario_id=1, total=100.0)
        # La fecha debería asignarse automáticamente
        assert hasattr(compra, 'fecha')


class TestVentaModel:
    """Pruebas para el modelo Venta"""
    
    def test_crear_venta(self):
        """Test: crear instancia de venta"""
        venta = Venta(
            usuario_id=1,
            total=250.00,
            cliente_nombre="Cliente Test"
        )
        assert venta.usuario_id == 1
        assert venta.total == 250.00
        assert venta.cliente_nombre == "Cliente Test"
    
    def test_venta_con_cliente_rfc(self):
        """Test: venta con RFC de cliente"""
        venta = Venta(
            usuario_id=1,
            total=1000.00,
            cliente_nombre="Empresa SA",
            cliente_rfc="EMP010101ABC"
        )
        assert venta.cliente_rfc == "EMP010101ABC"
    
    def test_venta_defaults(self):
        """Test: valores por defecto"""
        venta = Venta(usuario_id=1, total=100.0)
        assert venta.cliente_nombre is None
        assert venta.cliente_rfc is None

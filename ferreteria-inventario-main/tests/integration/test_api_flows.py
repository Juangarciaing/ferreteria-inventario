"""
Pruebas de integración - Flujos completos de la API
"""

import pytest
from app import create_app, db
from flask import json


@pytest.fixture
def client():
    """Cliente de prueba con base de datos temporal"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def auth_token(client):
    """Token de autenticación para pruebas"""
    from app.models.usuario import Usuario
    from app import db
    
    # Crear usuario de prueba directamente en la BD
    with client.application.app_context():
        admin_user = Usuario(
            nombre='Admin Test',
            email='admin@test.com',
            rol='admin',
            activo=1
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    
    data = json.loads(response.data)
    return data.get('data', {}).get('token') or data.get('token')


class TestProductoFlowCompleto:
    """Test: flujo completo de gestión de productos"""
    
    def test_flujo_completo_producto(self, client, auth_token):
        """Test: crear, leer, actualizar y eliminar producto"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 1. Crear categoría
        cat_response = client.post('/api/categorias', 
            json={'nombre': 'Herramientas', 'descripcion': 'Herramientas manuales'},
            headers=headers
        )
        assert cat_response.status_code in [200, 201]
        categoria_id = json.loads(cat_response.data)['data']['id']
        
        # 2. Crear producto
        prod_response = client.post('/api/productos',
            json={
                'nombre': 'Martillo',
                'descripcion': 'Martillo de acero',
                'precio': 150.00,
                'stock_actual': 20,
                'stock_minimo': 5,
                'categoria_id': categoria_id
            },
            headers=headers
        )
        assert prod_response.status_code in [200, 201]
        producto_id = json.loads(prod_response.data)['data']['id']
        
        # 3. Leer producto
        get_response = client.get(f'/api/productos/{producto_id}', headers=headers)
        assert get_response.status_code == 200
        producto = json.loads(get_response.data)['data']
        assert producto['nombre'] == 'Martillo'
        assert producto['precio'] == 150.00
        
        # 4. Actualizar producto
        update_response = client.put(f'/api/productos/{producto_id}',
            json={'precio': 175.00, 'stock_actual': 25},
            headers=headers
        )
        assert update_response.status_code == 200
        
        # Verificar actualización
        get_response2 = client.get(f'/api/productos/{producto_id}', headers=headers)
        producto_actualizado = json.loads(get_response2.data)['data']
        assert producto_actualizado['precio'] == 175.00
        assert producto_actualizado['stock_actual'] == 25
        
        # 5. Eliminar producto
        delete_response = client.delete(f'/api/productos/{producto_id}', headers=headers)
        assert delete_response.status_code == 200
        
        # Verificar eliminación
        get_response3 = client.get(f'/api/productos/{producto_id}', headers=headers)
        assert get_response3.status_code == 404


class TestVentaFlowCompleto:
    """Test: flujo completo de ventas"""
    
    def test_proceso_venta_completo(self, client, auth_token):
        """Test: crear venta y verificar descuento de stock"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 1. Preparar: crear categoría y producto
        cat_response = client.post('/api/categorias',
            json={'nombre': 'Materiales'},
            headers=headers
        )
        categoria_id = json.loads(cat_response.data)['data']['id']
        
        prod_response = client.post('/api/productos',
            json={
                'nombre': 'Cemento',
                'precio': 200.00,
                'stock_actual': 50,
                'stock_minimo': 10,
                'categoria_id': categoria_id
            },
            headers=headers
        )
        producto_id = json.loads(prod_response.data)['data']['id']
        
        # 2. Crear venta
        venta_response = client.post('/api/ventas',
            json={
                'detalles': [
                    {
                        'producto_id': producto_id,
                        'cantidad': 5,
                        'precio_unitario': 200.00
                    }
                ],
                'cliente_nombre': 'Juan Pérez',
                'cliente_rfc': 'PERJ800101ABC'
            },
            headers=headers
        )
        assert venta_response.status_code in [200, 201]
        venta_data = json.loads(venta_response.data)['data']
        assert venta_data['total'] == 1000.00
        
        # 3. Verificar descuento de stock
        get_prod_response = client.get(f'/api/productos/{producto_id}', headers=headers)
        producto_actual = json.loads(get_prod_response.data)['data']
        assert producto_actual['stock_actual'] == 45  # 50 - 5
    
    def test_venta_sin_stock_suficiente(self, client, auth_token):
        """Test: venta rechazada por stock insuficiente"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Preparar: producto con poco stock
        cat_response = client.post('/api/categorias',
            json={'nombre': 'Test'},
            headers=headers
        )
        categoria_id = json.loads(cat_response.data)['data']['id']
        
        prod_response = client.post('/api/productos',
            json={
                'nombre': 'Producto Limitado',
                'precio': 100.00,
                'stock_actual': 2,
                'stock_minimo': 1,
                'categoria_id': categoria_id
            },
            headers=headers
        )
        producto_id = json.loads(prod_response.data)['data']['id']
        
        # Intentar venta mayor al stock
        venta_response = client.post('/api/ventas',
            json={
                'detalles': [
                    {
                        'producto_id': producto_id,
                        'cantidad': 10,
                        'precio_unitario': 100.00
                    }
                ]
            },
            headers=headers
        )
        assert venta_response.status_code == 400


class TestCompraFlowCompleto:
    """Test: flujo completo de compras"""
    
    def test_proceso_compra_completo(self, client, auth_token):
        """Test: crear compra y verificar incremento de stock"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 1. Preparar datos
        cat_response = client.post('/api/categorias',
            json={'nombre': 'Eléctricos'},
            headers=headers
        )
        categoria_id = json.loads(cat_response.data)['data']['id']
        
        prov_response = client.post('/api/proveedores',
            json={
                'nombre': 'Proveedor Test',
                'telefono': '5512345678',
                'email': 'proveedor@test.com'
            },
            headers=headers
        )
        proveedor_id = json.loads(prov_response.data)['data']['id']
        
        prod_response = client.post('/api/productos',
            json={
                'nombre': 'Cable',
                'precio': 50.00,
                'stock_actual': 10,
                'stock_minimo': 5,
                'categoria_id': categoria_id
            },
            headers=headers
        )
        producto_id = json.loads(prod_response.data)['data']['id']
        
        # 2. Crear compra
        compra_response = client.post('/api/compras',
            json={
                'proveedor_id': proveedor_id,
                'detalles': [
                    {
                        'producto_id': producto_id,
                        'cantidad': 20,
                        'precio_unitario': 45.00
                    }
                ]
            },
            headers=headers
        )
        assert compra_response.status_code in [200, 201]
        compra_data = json.loads(compra_response.data)['data']
        assert compra_data['total'] == 900.00
        
        # 3. Verificar incremento de stock
        get_prod_response = client.get(f'/api/productos/{producto_id}', headers=headers)
        producto_actual = json.loads(get_prod_response.data)['data']
        assert producto_actual['stock_actual'] == 30  # 10 + 20


class TestBusquedaYFiltros:
    """Test: búsqueda y filtros"""
    
    def test_busqueda_productos(self, client, auth_token):
        """Test: búsqueda de productos por nombre"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Crear productos
        cat_response = client.post('/api/categorias',
            json={'nombre': 'Varios'},
            headers=headers
        )
        categoria_id = json.loads(cat_response.data)['data']['id']
        
        productos = [
            {'nombre': 'Martillo Grande', 'precio': 150, 'stock_actual': 10, 'stock_minimo': 5},
            {'nombre': 'Martillo Pequeño', 'precio': 100, 'stock_actual': 15, 'stock_minimo': 5},
            {'nombre': 'Destornillador', 'precio': 50, 'stock_actual': 20, 'stock_minimo': 5}
        ]
        
        for prod in productos:
            prod['categoria_id'] = categoria_id
            client.post('/api/productos', json=prod, headers=headers)
        
        # Buscar "martillo"
        search_response = client.get('/api/productos/search?q=martillo', headers=headers)
        assert search_response.status_code == 200
        resultados = json.loads(search_response.data)['data']
        assert len(resultados) == 2
        assert all('martillo' in r['nombre'].lower() for r in resultados)
    
    def test_productos_stock_bajo(self, client, auth_token):
        """Test: filtro de productos con stock bajo"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Crear productos con diferentes stocks
        cat_response = client.post('/api/categorias',
            json={'nombre': 'Test'},
            headers=headers
        )
        categoria_id = json.loads(cat_response.data)['data']['id']
        
        client.post('/api/productos',
            json={
                'nombre': 'Producto Stock Bajo',
                'precio': 100,
                'stock_actual': 3,
                'stock_minimo': 10,
                'categoria_id': categoria_id
            },
            headers=headers
        )
        
        client.post('/api/productos',
            json={
                'nombre': 'Producto Stock OK',
                'precio': 100,
                'stock_actual': 50,
                'stock_minimo': 10,
                'categoria_id': categoria_id
            },
            headers=headers
        )
        
        # Obtener productos con stock bajo
        response = client.get('/api/productos/stock-bajo', headers=headers)
        assert response.status_code == 200
        productos_bajo = json.loads(response.data)['data']
        assert len(productos_bajo) == 1
        assert productos_bajo[0]['nombre'] == 'Producto Stock Bajo'

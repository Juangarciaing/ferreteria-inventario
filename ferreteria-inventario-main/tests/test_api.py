"""
Tests básicos para el sistema de inventario
"""
import os
import pytest
from app import create_app, db
from app.models import Usuario, Producto, Categoria, Proveedor

# Variables de entorno para datos de prueba (con valores por defecto solo para testing local)
# En CI/CD, estas deberían venir de secrets seguros
TEST_ADMIN_EMAIL = os.environ.get('TEST_ADMIN_EMAIL', 'admin@test.com')
TEST_ADMIN_PASSWORD = os.environ.get('TEST_ADMIN_PASSWORD', 'test_admin_secure_pass_' + os.urandom(4).hex())
TEST_USER_EMAIL = os.environ.get('TEST_USER_EMAIL', 'test@test.com')
TEST_USER_PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'test_user_secure_pass_' + os.urandom(4).hex())


@pytest.fixture
def app():
    """Crea una instancia de la aplicación para testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Headers de autenticación para requests"""
    # Crear usuario admin de prueba
    from werkzeug.security import generate_password_hash
    from app import db
    from app.models import Usuario
    
    usuario = Usuario(
        nombre='Admin Test',
        email=TEST_ADMIN_EMAIL,
        password=generate_password_hash(TEST_ADMIN_PASSWORD),
        rol='admin'
    )
    db.session.add(usuario)
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': TEST_ADMIN_EMAIL,
        'password': TEST_ADMIN_PASSWORD
    })

    token = response.json['data']['token']
    return {'Authorization': f'Bearer {token}'}


class TestAuth:
    """Tests de autenticación"""
    
    def test_login_exitoso(self, client):
        """Test de login con credenciales válidas"""
        from werkzeug.security import generate_password_hash
        from app import db
        from app.models import Usuario
        
        usuario = Usuario(
            nombre='Test User',
            email=TEST_USER_EMAIL,
            password=generate_password_hash(TEST_USER_PASSWORD),
            rol='vendedor'
        )
        db.session.add(usuario)
        db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json
        assert 'data' in data
        assert 'token' in data['data']
    
    def test_login_fallido(self, client):
        """Test de login con credenciales inválidas"""
        response = client.post('/api/auth/login', json={
            'email': 'noexiste@test.com',
            'password': 'wrongpass'
        })

        assert response.status_code == 401
class TestProductos:
    """Tests de productos"""
    
    def test_crear_producto(self, client, auth_headers):
        """Test de creación de producto"""
        # Crear categoría primero
        from app.models import Categoria
        from app import db
        
        categoria = Categoria(nombre='Test Categoria', descripcion='Test')
        db.session.add(categoria)
        db.session.commit()
        
        response = client.post('/api/productos', 
            headers=auth_headers,
            json={
                'nombre': 'Martillo Test',
                'descripcion': 'Martillo de prueba',
                'precio': 15.50,
                'stock': 100,
                'stock_minimo': 10,
                'categoria_id': categoria.id
            }
        )
        
        assert response.status_code == 201
        assert 'id' in response.json
    
    def test_listar_productos(self, client, auth_headers):
        """Test de listado de productos"""
        response = client.get('/api/productos', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'data' in response.json
        assert isinstance(response.json['data'], list)
    
    def test_obtener_producto(self, client, auth_headers):
        """Test de obtener un producto específico"""
        # Crear producto de prueba
        from app.models import Producto, Categoria
        from app import db
        
        categoria = Categoria(nombre='Test', descripcion='Test')
        db.session.add(categoria)
        db.session.commit()
        
        producto = Producto(
            nombre='Producto Test',
            precio=10.0,
            stock=50,
            categoria_id=categoria.id
        )
        db.session.add(producto)
        db.session.commit()
        
        response = client.get(f'/api/productos/{producto.id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['nombre'] == 'Producto Test'


class TestCategorias:
    """Tests de categorías"""
    
    def test_crear_categoria(self, client, auth_headers):
        """Test de creación de categoría"""
        response = client.post('/api/categorias',
            headers=auth_headers,
            json={
                'nombre': 'Herramientas Test',
                'descripcion': 'Categoría de prueba'
            }
        )
        
        assert response.status_code == 201
    
    def test_listar_categorias(self, client, auth_headers):
        """Test de listado de categorías"""
        response = client.get('/api/categorias', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'data' in response.json
        assert isinstance(response.json['data'], list)


class TestVentas:
    """Tests de ventas"""
    
    def test_crear_venta(self, client, auth_headers):
        """Test de creación de venta"""
        # Crear producto y categoría
        from app.models import Producto, Categoria
        from app import db
        
        categoria = Categoria(nombre='Test', descripcion='Test')
        db.session.add(categoria)
        db.session.commit()
        
        producto = Producto(
            nombre='Producto Venta',
            precio=25.0,
            stock=100,
            categoria_id=categoria.id
        )
        db.session.add(producto)
        db.session.commit()
        
        response = client.post('/api/ventas',
            headers=auth_headers,
            json={
                'detalles': [
                    {
                        'producto_id': producto.id,
                        'cantidad': 2,
                        'precio_unitario': 25.0
                    }
                ],
                'cliente_nombre': 'Cliente Test',
                'cliente_documento': '12345678'
            }
        )
        
        assert response.status_code == 201
        assert 'id' in response.json


class TestProveedores:
    """Tests de proveedores"""
    
    def test_crear_proveedor(self, client, auth_headers):
        """Test de creación de proveedor"""
        response = client.post('/api/proveedores',
            headers=auth_headers,
            json={
                'nombre': 'Proveedor Test',
                'contacto': 'Juan Pérez',
                'telefono': '123456789',
                'email': 'proveedor@test.com'
            }
        )
        
        assert response.status_code == 201
    
    def test_listar_proveedores(self, client, auth_headers):
        """Test de listado de proveedores"""
        response = client.get('/api/proveedores', headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json, list)


class TestValidaciones:
    """Tests de validaciones"""
    
    def test_producto_sin_nombre(self, client, auth_headers):
        """Test de validación: producto sin nombre"""
        response = client.post('/api/productos',
            headers=auth_headers,
            json={
                'precio': 10.0,
                'stock': 50
            }
        )
        
        assert response.status_code == 400
    
    def test_precio_negativo(self, client, auth_headers):
        """Test de validación: precio negativo"""
        from app.models import Categoria
        from app import db
        
        categoria = Categoria(nombre='Test', descripcion='Test')
        db.session.add(categoria)
        db.session.commit()
        
        response = client.post('/api/productos',
            headers=auth_headers,
            json={
                'nombre': 'Producto',
                'precio': -10.0,
                'stock': 50,
                'categoria_id': categoria.id
            }
        )
        
        assert response.status_code == 400


class TestCache:
    """Tests de caché"""
    
    def test_cache_categorias(self, client, auth_headers):
        """Test de caché en categorías"""
        # Primera llamada (sin caché)
        response1 = client.get('/api/categorias', headers=auth_headers)
        
        # Segunda llamada (con caché)
        response2 = client.get('/api/categorias', headers=auth_headers)
        
        assert response1.json == response2.json

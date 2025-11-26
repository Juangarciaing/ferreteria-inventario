"""
Configuración de pytest con base de datos temporal
"""

import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.usuario import Usuario, RolUsuario
from app.models.producto import Producto, Categoria
from app.models.proveedor import Proveedor


@pytest.fixture(scope='session')
def app():
    """
    Fixture de aplicación Flask para toda la sesión de pruebas.
    Usa SQLite en memoria para no afectar la base de datos real.
    """
    app = create_app()
    
    # Configuración para pruebas con base de datos temporal
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Base de datos en memoria
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False,
    })
    
    return app


@pytest.fixture(scope='function')
def client(app):
    """
    Cliente de prueba Flask.
    Cada test obtiene una base de datos limpia.
    """
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario de prueba por defecto
        admin_user = Usuario(
            nombre='Admin Test',
            email='admin@test.com',
            rol=RolUsuario.ADMIN,
            activo=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Crear datos básicos de prueba
        categoria_test = Categoria(
            nombre='Categoría Test',
            descripcion='Categoría para pruebas',
            activo=True
        )
        db.session.add(categoria_test)
        
        proveedor_test = Proveedor(
            nombre='Proveedor Test',
            telefono='5512345678',
            email='proveedor@test.com',
            activo=True
        )
        db.session.add(proveedor_test)
        
        db.session.commit()
        
        # Crear cliente de prueba
        with app.test_client() as client:
            yield client
        
        # Limpiar base de datos después de cada test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def auth_token(client):
    """
    Fixture que proporciona un token de autenticación válido.
    """
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    
    if response.status_code == 200:
        data = response.get_json()
        token = data.get('data', {}).get('token') or data.get('token')
        return token
    
    raise Exception('No se pudo obtener token de autenticación en pruebas')


@pytest.fixture(scope='function')
def auth_headers(auth_token):
    """
    Fixture que proporciona headers con autenticación.
    """
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope='function')
def sample_categoria(client, auth_headers):
    """
    Fixture que crea una categoría de ejemplo.
    """
    response = client.post('/api/categorias', 
        json={
            'nombre': 'Herramientas',
            'descripcion': 'Herramientas manuales y eléctricas'
        },
        headers=auth_headers
    )
    
    if response.status_code in [200, 201]:
        return response.get_json()['data']
    
    return None


@pytest.fixture(scope='function')
def sample_producto(client, auth_headers, sample_categoria):
    """
    Fixture que crea un producto de ejemplo.
    """
    response = client.post('/api/productos',
        json={
            'nombre': 'Martillo Test',
            'descripcion': 'Martillo de prueba',
            'precio': 150.00,
            'stock_actual': 20,
            'stock_minimo': 5,
            'categoria_id': sample_categoria['id']
        },
        headers=auth_headers
    )
    
    if response.status_code in [200, 201]:
        return response.get_json()['data']
    
    return None


@pytest.fixture(scope='function')
def sample_proveedor(client, auth_headers):
    """
    Fixture que crea un proveedor de ejemplo.
    """
    response = client.post('/api/proveedores',
        json={
            'nombre': 'Proveedor Ejemplo',
            'telefono': '5598765432',
            'email': 'proveedor@ejemplo.com',
            'direccion': 'Calle Test 123'
        },
        headers=auth_headers
    )
    
    if response.status_code in [200, 201]:
        return response.get_json()['data']
    
    return None


# Configuración de pytest-cov
def pytest_configure(config):
    """Configuración adicional de pytest."""
    config.addinivalue_line(
        "markers", "slow: marca tests que son lentos"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios"
    )

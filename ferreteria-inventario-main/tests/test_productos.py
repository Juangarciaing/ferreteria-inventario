"""
Tests para productos
"""
import unittest
import json
from app import create_app, db
from app.models import Usuario, Producto, Categoria

class TestProductos(unittest.TestCase):
    def setUp(self):
        """Configurar test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Crear tablas
        db.create_all()
        
        # Crear usuario admin
        self.admin_user = Usuario(
            nombre='Admin',
            email='admin@test.com',
            rol='admin'
        )
        self.admin_user.set_password('admin123')
        db.session.add(self.admin_user)
        
        # Crear categoría
        self.categoria = Categoria(nombre='Herramientas')
        db.session.add(self.categoria)
        
        db.session.commit()
        
        # Obtener token
        login_response = self.client.post('/api/auth/login', 
            json={'email': 'admin@test.com', 'password': 'admin123'})
        self.token = json.loads(login_response.data)['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def tearDown(self):
        """Limpiar después del test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_producto(self):
        """Test crear producto"""
        producto_data = {
            'nombre': 'Martillo Test',
            'descripcion': 'Martillo de prueba',
            'precio': 25.99,
            'stock': 10,
            'stock_minimo': 5,
            'categoria_id': self.categoria.id
        }
        
        response = self.client.post('/api/productos', 
            json=producto_data, headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
    
    def test_get_productos(self):
        """Test obtener productos"""
        # Crear producto de prueba
        producto = Producto(
            nombre='Test Product',
            precio=10.99,
            stock=5,
            categoria_id=self.categoria.id
        )
        db.session.add(producto)
        db.session.commit()
        
        response = self.client.get('/api/productos', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
    
    def test_update_producto(self):
        """Test actualizar producto"""
        # Crear producto
        producto = Producto(
            nombre='Test Product',
            precio=10.99,
            stock=5,
            categoria_id=self.categoria.id
        )
        db.session.add(producto)
        db.session.commit()
        
        # Actualizar producto
        update_data = {'nombre': 'Updated Product', 'precio': 15.99}
        response = self.client.put(f'/api/productos/{producto.id}', 
            json=update_data, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_delete_producto(self):
        """Test eliminar producto"""
        # Crear producto
        producto = Producto(
            nombre='Test Product',
            precio=10.99,
            stock=5,
            categoria_id=self.categoria.id
        )
        db.session.add(producto)
        db.session.commit()
        
        # Eliminar producto
        response = self.client.delete(f'/api/productos/{producto.id}', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_search_productos(self):
        """Test buscar productos"""
        # Crear productos de prueba
        producto1 = Producto(
            nombre='Martillo Test',
            precio=10.99,
            stock=5,
            categoria_id=self.categoria.id
        )
        producto2 = Producto(
            nombre='Destornillador Test',
            precio=5.99,
            stock=10,
            categoria_id=self.categoria.id
        )
        db.session.add_all([producto1, producto2])
        db.session.commit()
        
        # Buscar productos
        response = self.client.get('/api/productos/search?q=martillo', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Martillo Test')
    
    def test_productos_stock_bajo(self):
        """Test productos con stock bajo"""
        # Crear producto con stock bajo
        producto = Producto(
            nombre='Low Stock Product',
            precio=10.99,
            stock=2,
            stock_minimo=5,
            categoria_id=self.categoria.id
        )
        db.session.add(producto)
        db.session.commit()
        
        response = self.client.get('/api/productos/stock-bajo', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Low Stock Product')

if __name__ == '__main__':
    unittest.main()

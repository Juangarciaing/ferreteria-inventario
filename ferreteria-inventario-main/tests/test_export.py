"""
Tests para exportación
"""
import unittest
import json
from app import create_app, db
from app.models import Usuario, Producto, Categoria

class TestExport(unittest.TestCase):
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
        db.session.flush()  # Flush to get the ID
        
        # Crear producto
        self.producto = Producto(
            nombre='Test Product',
            precio=10.99,
            stock=5,
            categoria_id=self.categoria.id
        )
        db.session.add(self.producto)
        
        db.session.commit()
        
        # Obtener token
        login_response = self.client.post('/api/auth/login', 
            json={'email': 'admin@test.com', 'password': 'admin123'})
        response_data = json.loads(login_response.data)
        self.token = response_data['data']['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def tearDown(self):
        """Limpiar después del test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_export_productos_pdf(self):
        """Test exportar productos a PDF"""
        response = self.client.get('/api/export/productos?format=pdf', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
    
    def test_export_productos_excel(self):
        """Test exportar productos a Excel"""
        response = self.client.get('/api/export/productos?format=excel', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
    
    def test_export_productos_csv(self):
        """Test exportar productos a CSV"""
        response = self.client.get('/api/export/productos?format=csv',
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.content_type)
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
    
    def test_export_categorias(self):
        """Test exportar categorías"""
        response = self.client.get('/api/export/categorias?format=pdf', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
    
    def test_export_with_filters(self):
        """Test exportar con filtros"""
        response = self.client.get('/api/export/productos?format=pdf&categoria_id=1', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
    
    def test_export_stock_bajo(self):
        """Test exportar productos con stock bajo"""
        # Crear producto con stock bajo
        producto_bajo = Producto(
            nombre='Low Stock Product',
            precio=5.99,
            stock=2,
            stock_minimo=5,
            categoria_id=self.categoria.id
        )
        db.session.add(producto_bajo)
        db.session.commit()
        
        response = self.client.get('/api/export/productos?format=pdf&stock_bajo=true', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
    
    def test_export_invalid_format(self):
        """Test exportar con formato inválido"""
        response = self.client.get('/api/export/productos?format=invalid', 
            headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_export_access_control(self):
        """Test control de acceso para exportación"""
        # Crear usuario vendedor
        vendedor = Usuario(
            nombre='Vendedor',
            email='vendedor@test.com',
            rol='vendedor'
        )
        vendedor.set_password('vendedor123')
        db.session.add(vendedor)
        db.session.commit()
        
        # Login como vendedor
        login_response = self.client.post('/api/auth/login', 
            json={'email': 'vendedor@test.com', 'password': 'vendedor123'})
        response_data = json.loads(login_response.data)
        vendedor_token = response_data['data']['token']
        vendedor_headers = {'Authorization': f'Bearer {vendedor_token}'}
        
        # Intentar exportar productos (debería funcionar)
        response = self.client.get('/api/export/productos?format=pdf', 
            headers=vendedor_headers)
        self.assertEqual(response.status_code, 200)
        
        # Intentar exportar usuarios (debería fallar)
        response = self.client.get('/api/export/usuarios?format=pdf', 
            headers=vendedor_headers)
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()

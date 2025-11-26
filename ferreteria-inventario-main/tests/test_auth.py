"""
Tests para autenticación
"""
import unittest
import json
from app import create_app, db
from app.models import Usuario

class TestAuth(unittest.TestCase):
    def setUp(self):
        """Configurar test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Crear tablas
        db.create_all()
        
        # Crear usuario de prueba
        self.test_user = Usuario(
            nombre='Test User',
            email='test@test.com',
            rol='vendedor'
        )
        self.test_user.set_password('test123')
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """Limpiar después del test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_success(self):
        """Test login exitoso"""
        response = self.client.post('/api/auth/login', 
            json={'email': 'test@test.com', 'password': 'test123'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'test@test.com')
    
    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        response = self.client.post('/api/auth/login', 
            json={'email': 'test@test.com', 'password': 'wrong'})
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_login_missing_fields(self):
        """Test login con campos faltantes"""
        response = self.client.post('/api/auth/login', 
            json={'email': 'test@test.com'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_protected_route_without_token(self):
        """Test ruta protegida sin token"""
        response = self.client.get('/api/productos')
        self.assertEqual(response.status_code, 401)
    
    def test_protected_route_with_token(self):
        """Test ruta protegida con token válido"""
        # Login para obtener token
        login_response = self.client.post('/api/auth/login', 
            json={'email': 'test@test.com', 'password': 'test123'})
        token = json.loads(login_response.data)['token']
        
        # Usar token para acceder a ruta protegida
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/productos', headers=headers)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

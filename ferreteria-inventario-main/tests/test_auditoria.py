"""
Tests para auditoría
"""
import unittest
import json
from app import create_app, db
from app.models import Usuario
from app.models.auditoria import AuditoriaLog

class TestAuditoria(unittest.TestCase):
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
    
    def test_get_auditoria_logs(self):
        """Test obtener logs de auditoría"""
        # Crear log de prueba
        log = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='test_action',
            tabla_afectada='test_table',
            registro_id='1',
            datos_nuevos={'test': 'data'}
        )
        db.session.add(log)
        db.session.commit()
        
        response = self.client.get('/api/auditoria/logs', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('logs', data)
        self.assertIn('total', data)
        self.assertIsInstance(data['logs'], list)
    
    def test_get_logs_usuario(self):
        """Test obtener logs de usuario específico"""
        # Crear log de prueba
        log = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='test_action',
            tabla_afectada='test_table',
            registro_id='1'
        )
        db.session.add(log)
        db.session.commit()
        
        response = self.client.get(f'/api/auditoria/logs/usuario/{self.admin_user.id}', 
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
    
    def test_get_logs_tabla(self):
        """Test obtener logs de tabla específica"""
        # Crear log de prueba
        log = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='test_action',
            tabla_afectada='productos',
            registro_id='1'
        )
        db.session.add(log)
        db.session.commit()
        
        response = self.client.get('/api/auditoria/logs/tabla/productos', 
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
    
    def test_get_logs_registro(self):
        """Test obtener historial de registro"""
        # Crear logs de prueba
        log1 = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='create',
            tabla_afectada='productos',
            registro_id='1',
            datos_nuevos={'nombre': 'Producto 1'}
        )
        log2 = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='update',
            tabla_afectada='productos',
            registro_id='1',
            datos_anteriores={'nombre': 'Producto 1'},
            datos_nuevos={'nombre': 'Producto 1 Actualizado'}
        )
        db.session.add_all([log1, log2])
        db.session.commit()
        
        response = self.client.get('/api/auditoria/logs/registro/productos/1', 
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
    
    def test_generar_reporte_auditoria(self):
        """Test generar reporte de auditoría"""
        # Crear logs de prueba
        log = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='test_action',
            tabla_afectada='test_table',
            registro_id='1'
        )
        db.session.add(log)
        db.session.commit()
        
        response = self.client.get('/api/auditoria/reporte?fecha_inicio=2024-01-01&fecha_fin=2024-12-31', 
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('logs', data)
        self.assertIn('estadisticas', data)
        self.assertIn('periodo', data)
    
    def test_estadisticas_auditoria(self):
        """Test obtener estadísticas de auditoría"""
        # Crear logs de prueba
        log = AuditoriaLog(
            usuario_id=self.admin_user.id,
            accion='test_action',
            tabla_afectada='test_table',
            registro_id='1'
        )
        db.session.add(log)
        db.session.commit()
        
        response = self.client.get('/api/auditoria/estadisticas', 
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_logs', data)
        self.assertIn('acciones_mas_comunes', data)
        self.assertIn('usuarios_mas_activos', data)
    
    def test_auditoria_access_control(self):
        """Test control de acceso a auditoría"""
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
        vendedor_token = json.loads(login_response.data)['token']
        vendedor_headers = {'Authorization': f'Bearer {vendedor_token}'}
        
        # Intentar acceder a auditoría
        response = self.client.get('/api/auditoria/logs', headers=vendedor_headers)
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()

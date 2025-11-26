"""
Configuración de tests
"""
import os
import tempfile
from app import create_app, db

class TestConfig:
    """Configuración para tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = False  # No expira en tests
    WTF_CSRF_ENABLED = False
    CORS_ORIGINS = ['http://localhost:3000']
    
    # Configuración de auditoría para tests
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_LEVEL = 'INFO'
    
    # Configuración de exportación para tests
    EXPORT_MAX_RECORDS = 1000
    EXPORT_FORMATS = ['pdf', 'excel', 'csv']
    
    # Configuración de notificaciones para tests
    NOTIFICATIONS_ENABLED = True
    NOTIFICATION_RETENTION_DAYS = 30

def create_test_app():
    """Crear aplicación para tests"""
    app = create_app('testing')
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def setup_test_db():
    """Configurar base de datos para tests"""
    db.create_all()

def teardown_test_db():
    """Limpiar base de datos después de tests"""
    db.drop_all()

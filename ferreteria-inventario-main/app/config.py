"""
Configuración centralizada de la aplicación Flask
"""
import os
from datetime import timedelta

class Config:
    """Configuración base"""
    # SEGURIDAD: Las claves secretas DEBEN configurarse en variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY no está configurada. Define la variable de entorno SECRET_KEY")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost/ferreteria_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS Configuration (permite override por env CORS_ORIGINS separadas por comas)
    _cors_env = os.environ.get('CORS_ORIGINS')
    if _cors_env:
        CORS_ORIGINS = [o.strip() for o in _cors_env.split(',') if o.strip()]
    else:
        CORS_ORIGINS = [
            'http://localhost:5173', 
            'http://localhost:5174', 
            'http://localhost:5175',
            'http://localhost:5176',
            'http://localhost:3000'
        ]

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    # Cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # En producción usar Redis
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_TYPE = 'SimpleCache'
    RATELIMIT_STORAGE_URL = 'memory://'

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
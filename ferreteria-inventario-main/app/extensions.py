"""
Extensiones de Flask para cache, limiter, etc.
Configuración centralizada de extensiones
"""
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuración de caché
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',  # En producción usar Redis
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutos por defecto
})

# Configuración de rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000 per day", "1000 per hour"],  # Límites permisivos para desarrollo
    storage_uri="memory://",  # En producción usar Redis
)

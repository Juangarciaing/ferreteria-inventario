"""
Sistema de monitoreo para la aplicación
"""
import time
import psutil
import logging
from datetime import datetime, timedelta
from flask import request, g, current_app
from functools import wraps
from app import db
from app.models.auditoria import AuditoriaLog

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor del sistema"""
    
    def __init__(self):
        self.metrics = {
            'requests_count': 0,
            'requests_time': [],
            'errors_count': 0,
            'active_users': set(),
            'memory_usage': [],
            'cpu_usage': [],
            'disk_usage': []
        }
    
    def record_request(self, endpoint, method, status_code, response_time):
        """Registrar una petición"""
        self.metrics['requests_count'] += 1
        self.metrics['requests_time'].append(response_time)
        
        # Mantener solo los últimos 1000 tiempos de respuesta
        if len(self.metrics['requests_time']) > 1000:
            self.metrics['requests_time'] = self.metrics['requests_time'][-1000:]
        
        # Log de la petición
        logger.info(f"Request: {method} {endpoint} - Status: {status_code} - Time: {response_time:.3f}s")
    
    def record_error(self, error_type, error_message):
        """Registrar un error"""
        self.metrics['errors_count'] += 1
        logger.error(f"Error: {error_type} - {error_message}")
    
    def record_active_user(self, user_id):
        """Registrar usuario activo"""
        self.metrics['active_users'].add(user_id)
    
    def remove_active_user(self, user_id):
        """Remover usuario activo"""
        self.metrics['active_users'].discard(user_id)
    
    def get_system_metrics(self):
        """Obtener métricas del sistema"""
        try:
            # Métricas del sistema
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Actualizar métricas
            self.metrics['memory_usage'].append({
                'timestamp': datetime.now().isoformat(),
                'used_percent': memory.percent,
                'used_gb': memory.used / (1024**3),
                'available_gb': memory.available / (1024**3)
            })
            
            self.metrics['cpu_usage'].append({
                'timestamp': datetime.now().isoformat(),
                'percent': cpu
            })
            
            self.metrics['disk_usage'].append({
                'timestamp': datetime.now().isoformat(),
                'used_percent': (disk.used / disk.total) * 100,
                'used_gb': disk.used / (1024**3),
                'total_gb': disk.total / (1024**3)
            })
            
            # Mantener solo las últimas 100 métricas
            for key in ['memory_usage', 'cpu_usage', 'disk_usage']:
                if len(self.metrics[key]) > 100:
                    self.metrics[key] = self.metrics[key][-100:]
            
            return {
                'memory': {
                    'used_percent': memory.percent,
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2)
                },
                'cpu': {
                    'percent': cpu
                },
                'disk': {
                    'used_percent': round((disk.used / disk.total) * 100, 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'total_gb': round(disk.total / (1024**3), 2)
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo métricas del sistema: {e}")
            return None
    
    def get_performance_metrics(self):
        """Obtener métricas de rendimiento"""
        if not self.metrics['requests_time']:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'total_requests': 0,
                'error_rate': 0
            }
        
        times = self.metrics['requests_time']
        total_requests = self.metrics['requests_count']
        errors = self.metrics['errors_count']
        
        return {
            'avg_response_time': round(sum(times) / len(times), 3),
            'min_response_time': round(min(times), 3),
            'max_response_time': round(max(times), 3),
            'total_requests': total_requests,
            'error_rate': round((errors / total_requests) * 100, 2) if total_requests > 0 else 0
        }
    
    def get_active_users_count(self):
        """Obtener número de usuarios activos"""
        return len(self.metrics['active_users'])
    
    def get_health_status(self):
        """Obtener estado de salud del sistema"""
        system_metrics = self.get_system_metrics()
        performance_metrics = self.get_performance_metrics()
        
        if not system_metrics:
            return {'status': 'error', 'message': 'No se pudieron obtener métricas del sistema'}
        
        # Verificar umbrales de salud
        health_issues = []
        
        if system_metrics['memory']['used_percent'] > 90:
            health_issues.append('Alto uso de memoria')
        
        if system_metrics['cpu']['percent'] > 90:
            health_issues.append('Alto uso de CPU')
        
        if system_metrics['disk']['used_percent'] > 90:
            health_issues.append('Alto uso de disco')
        
        if performance_metrics['error_rate'] > 10:
            health_issues.append('Alta tasa de errores')
        
        if performance_metrics['avg_response_time'] > 2.0:
            health_issues.append('Tiempo de respuesta lento')
        
        status = 'healthy' if not health_issues else 'warning' if len(health_issues) < 3 else 'critical'
        
        return {
            'status': status,
            'issues': health_issues,
            'system_metrics': system_metrics,
            'performance_metrics': performance_metrics,
            'active_users': self.get_active_users_count(),
            'timestamp': datetime.now().isoformat()
        }

# Instancia global del monitor
monitor = SystemMonitor()

def monitor_request(f):
    """Decorador para monitorear peticiones"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            # Ejecutar la función
            response = f(*args, **kwargs)
            
            # Calcular tiempo de respuesta
            response_time = time.time() - start_time
            
            # Registrar la petición
            monitor.record_request(
                endpoint=request.endpoint or 'unknown',
                method=request.method,
                status_code=getattr(response, 'status_code', 200),
                response_time=response_time
            )
            
            return response
            
        except Exception as e:
            # Registrar error
            response_time = time.time() - start_time
            monitor.record_error(type(e).__name__, str(e))
            
            # Re-lanzar la excepción
            raise
    
    return decorated_function

def monitor_database_operations(f):
    """Decorador para monitorear operaciones de base de datos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            # Ejecutar la función
            result = f(*args, **kwargs)
            
            # Calcular tiempo de operación
            operation_time = time.time() - start_time
            
            # Log de operación de BD
            logger.info(f"Database operation: {f.__name__} - Time: {operation_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Log de error de BD
            operation_time = time.time() - start_time
            logger.error(f"Database error in {f.__name__}: {e} - Time: {operation_time:.3f}s")
            raise
    
    return decorated_function

def get_monitoring_data():
    """Obtener datos de monitoreo"""
    return {
        'system_health': monitor.get_health_status(),
        'performance': monitor.get_performance_metrics(),
        'system_metrics': monitor.get_system_metrics(),
        'active_users': monitor.get_active_users_count(),
        'total_requests': monitor.metrics['requests_count'],
        'total_errors': monitor.metrics['errors_count']
    }

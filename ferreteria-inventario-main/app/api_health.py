"""
Health Check y Monitoring Endpoints
Verifica el estado de la aplicación y sus dependencias
"""
from flask import Blueprint, jsonify
from datetime import datetime
import os
import psutil
from app import db
from app.models import Producto, Venta, Compra, Usuario, Proveedor

health_bp = Blueprint('health', __name__, url_prefix='/api/health')

@health_bp.route('', methods=['GET'])
def health_check():
    """
    Endpoint básico de health check
    Verifica que la aplicación esté viva
    
    Returns:
        200 OK si la app está funcionando
    
    Example:
        GET /api/health
        Response: {
            "status": "healthy",
            "timestamp": "2025-11-12 10:30:00",
            "service": "Ferretería API"
        }
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service": "Ferretería API",
        "version": "1.0.0"
    }), 200


@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """
    Health check detallado con verificación de dependencias
    
    Verifica:
    - Base de datos (conexión y lectura)
    - Uso de memoria
    - Uso de CPU
    - Espacio en disco
    
    Returns:
        200 OK si todo está bien
        503 Service Unavailable si hay problemas
    
    Example:
        GET /api/health/detailed
        Response: {
            "status": "healthy",
            "timestamp": "2025-11-12 10:30:00",
            "checks": {
                "database": "healthy",
                "memory": "healthy",
                "cpu": "healthy",
                "disk": "healthy"
            },
            "details": {...}
        }
    """
    checks = {}
    overall_status = "healthy"
    
    # ===== VERIFICAR BASE DE DATOS =====
    try:
        # Intentar ejecutar una query simple
        db.session.execute(db.text('SELECT 1'))
        db.session.commit()
        checks['database'] = {
            "status": "healthy",
            "message": "Conexión exitosa"
        }
    except Exception as e:
        checks['database'] = {
            "status": "unhealthy",
            "message": f"Error de conexión: {str(e)}"
        }
        overall_status = "unhealthy"
    
    # ===== VERIFICAR MEMORIA =====
    try:
        memory = psutil.virtual_memory()
        memory_usage_percent = memory.percent
        
        if memory_usage_percent < 80:
            memory_status = "healthy"
        elif memory_usage_percent < 90:
            memory_status = "warning"
        else:
            memory_status = "critical"
            overall_status = "degraded" if overall_status == "healthy" else overall_status
        
        checks['memory'] = {
            "status": memory_status,
            "usage_percent": round(memory_usage_percent, 2),
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2)
        }
    except Exception as e:
        checks['memory'] = {
            "status": "unknown",
            "message": f"No se pudo verificar: {str(e)}"
        }
    
    # ===== VERIFICAR CPU =====
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent < 70:
            cpu_status = "healthy"
        elif cpu_percent < 85:
            cpu_status = "warning"
        else:
            cpu_status = "critical"
            overall_status = "degraded" if overall_status == "healthy" else overall_status
        
        checks['cpu'] = {
            "status": cpu_status,
            "usage_percent": round(cpu_percent, 2),
            "cores": psutil.cpu_count()
        }
    except Exception as e:
        checks['cpu'] = {
            "status": "unknown",
            "message": f"No se pudo verificar: {str(e)}"
        }
    
    # ===== VERIFICAR DISCO =====
    try:
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        if disk_usage_percent < 80:
            disk_status = "healthy"
        elif disk_usage_percent < 90:
            disk_status = "warning"
        else:
            disk_status = "critical"
            overall_status = "degraded" if overall_status == "healthy" else overall_status
        
        checks['disk'] = {
            "status": disk_status,
            "usage_percent": round(disk_usage_percent, 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2)
        }
    except Exception as e:
        checks['disk'] = {
            "status": "unknown",
            "message": f"No se pudo verificar: {str(e)}"
        }
    
    # Código de respuesta basado en estado
    status_code = 200
    if overall_status == "unhealthy":
        status_code = 503
    elif overall_status == "degraded":
        status_code = 200  # Funciona pero con advertencias
    
    return jsonify({
        "status": overall_status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service": "Ferretería API",
        "version": "1.0.0",
        "checks": checks
    }), status_code


@health_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Estadísticas generales del sistema
    Muestra contadores de las entidades principales
    
    Returns:
        Estadísticas de productos, ventas, compras, usuarios, proveedores
    
    Example:
        GET /api/health/stats
        Response: {
            "timestamp": "2025-11-12 10:30:00",
            "database": {
                "productos": 150,
                "ventas": 1250,
                "compras": 380,
                "usuarios": 12,
                "proveedores": 25
            },
            "uptime": "2 days, 5 hours"
        }
    """
    try:
        # Calcular uptime (tiempo desde que inició el proceso)
        process = psutil.Process(os.getpid())
        uptime_seconds = datetime.now().timestamp() - process.create_time()
        uptime_days = int(uptime_seconds // 86400)
        uptime_hours = int((uptime_seconds % 86400) // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        uptime_str = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
        
        stats = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "database": {
                "productos": Producto.query.count(),
                "ventas": Venta.query.count(),
                "compras": Compra.query.count(),
                "usuarios": Usuario.query.count(),
                "proveedores": Proveedor.query.count()
            },
            "system": {
                "uptime": uptime_str,
                "process_id": os.getpid(),
                "memory_mb": round(process.memory_info().rss / (1024**2), 2)
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({
            "error": f"No se pudieron obtener estadísticas: {str(e)}"
        }), 500


@health_bp.route('/ping', methods=['GET'])
def ping():
    """
    Endpoint simple de ping/pong
    Útil para verificar que el servidor responde
    
    Returns:
        "pong" con timestamp
    
    Example:
        GET /api/health/ping
        Response: {
            "message": "pong",
            "timestamp": "2025-11-12 10:30:00"
        }
    """
    return jsonify({
        "message": "pong",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200

"""
Endpoints para monitoreo del sistema
"""
from flask import Blueprint, request, jsonify
from app.api_routes import token_required, rol_requerido
from app.utils.monitoring import get_monitoring_data, monitor
from datetime import datetime, timedelta
import logging

monitoring_api = Blueprint('monitoring_api', __name__, url_prefix='/api')

@monitoring_api.route('/monitoring/health', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_system_health(current_user):
    """Obtener estado de salud del sistema (solo admin)"""
    try:
        health_data = monitor.get_health_status()
        return jsonify(health_data), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener estado de salud', 'detail': str(e)}), 500

@monitoring_api.route('/monitoring/metrics', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_system_metrics(current_user):
    """Obtener métricas del sistema (solo admin)"""
    try:
        metrics_data = get_monitoring_data()
        return jsonify(metrics_data), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener métricas', 'detail': str(e)}), 500

@monitoring_api.route('/monitoring/performance', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_performance_metrics(current_user):
    """Obtener métricas de rendimiento (solo admin)"""
    try:
        performance_data = monitor.get_performance_metrics()
        return jsonify(performance_data), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener métricas de rendimiento', 'detail': str(e)}), 500

@monitoring_api.route('/monitoring/system', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_system_info(current_user):
    """Obtener información del sistema (solo admin)"""
    try:
        system_metrics = monitor.get_system_metrics()
        return jsonify(system_metrics), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener información del sistema', 'detail': str(e)}), 500

@monitoring_api.route('/monitoring/alerts', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_system_alerts(current_user):
    """Obtener alertas del sistema (solo admin)"""
    try:
        health_data = monitor.get_health_status()
        
        alerts = []
        
        # Verificar alertas de memoria
        if health_data.get('system_metrics', {}).get('memory', {}).get('used_percent', 0) > 80:
            alerts.append({
                'type': 'warning',
                'category': 'memory',
                'message': 'Uso de memoria alto',
                'value': f"{health_data['system_metrics']['memory']['used_percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar alertas de CPU
        if health_data.get('system_metrics', {}).get('cpu', {}).get('percent', 0) > 80:
            alerts.append({
                'type': 'warning',
                'category': 'cpu',
                'message': 'Uso de CPU alto',
                'value': f"{health_data['system_metrics']['cpu']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar alertas de disco
        if health_data.get('system_metrics', {}).get('disk', {}).get('used_percent', 0) > 80:
            alerts.append({
                'type': 'warning',
                'category': 'disk',
                'message': 'Uso de disco alto',
                'value': f"{health_data['system_metrics']['disk']['used_percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar alertas de rendimiento
        performance = health_data.get('performance_metrics', {})
        if performance.get('error_rate', 0) > 5:
            alerts.append({
                'type': 'error',
                'category': 'performance',
                'message': 'Tasa de errores alta',
                'value': f"{performance['error_rate']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if performance.get('avg_response_time', 0) > 1.0:
            alerts.append({
                'type': 'warning',
                'category': 'performance',
                'message': 'Tiempo de respuesta lento',
                'value': f"{performance['avg_response_time']:.3f}s",
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'alerts': alerts,
            'total_alerts': len(alerts),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener alertas', 'detail': str(e)}), 500

@monitoring_api.route('/monitoring/logs', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_system_logs(current_user):
    """Obtener logs del sistema (solo admin)"""
    try:
        # Obtener logs de auditoría recientes
        from app.models.auditoria import AuditoriaLog
        
        # Logs de las últimas 24 horas
        since = datetime.now() - timedelta(hours=24)
        logs = AuditoriaLog.query.filter(
            AuditoriaLog.created_at >= since
        ).order_by(AuditoriaLog.created_at.desc()).limit(100).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'timestamp': log.created_at.isoformat(),
                'level': 'info',
                'message': f"{log.accion} en {log.tabla_afectada}",
                'user': log.usuario.nombre if log.usuario else 'Sistema',
                'ip': log.ip_address,
                'details': {
                    'action': log.accion,
                    'table': log.tabla_afectada,
                    'record_id': log.registro_id
                }
            })
        
        return jsonify({
            'logs': logs_data,
            'total': len(logs_data),
            'since': since.isoformat(),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener logs', 'detail': str(e)}), 500

@monitoring_api.route('/monitoring/status', methods=['GET'])
def get_system_status():
    """Obtener estado básico del sistema (público)"""
    try:
        # Verificar conectividad de BD
        from app import db
        db.session.execute('SELECT 1')
        
        # Obtener métricas básicas
        health_data = monitor.get_health_status()
        
        return jsonify({
            'status': 'online',
            'database': 'connected',
            'uptime': 'running',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'health': health_data.get('status', 'unknown')
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'uptime': 'unknown',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

"""
Endpoints de auditoría y logs
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app.api_routes import token_required, rol_requerido
from app.models.auditoria import AuditoriaLog
from app import db

auditoria_api = Blueprint('auditoria_api', __name__, url_prefix='/api')

@auditoria_api.route('/auditoria/logs', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_auditoria_logs(current_user):
    """Obtener logs de auditoría (solo admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        usuario_id = request.args.get('usuario_id', type=int)
        accion = request.args.get('accion')
        tabla = request.args.get('tabla')
        
        # Filtros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        query = AuditoriaLog.query
        
        # Aplicar filtros
        if usuario_id:
            query = query.filter(AuditoriaLog.usuario_id == usuario_id)
        if accion:
            query = query.filter(AuditoriaLog.accion == accion)
        if tabla:
            query = query.filter(AuditoriaLog.tabla_afectada == tabla)
        if fecha_inicio:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            query = query.filter(AuditoriaLog.created_at >= fecha_inicio)
        if fecha_fin:
            fecha_fin = datetime.fromisoformat(fecha_fin)
            query = query.filter(AuditoriaLog.created_at <= fecha_fin)
        
        # Paginación
        logs = query.order_by(AuditoriaLog.created_at.desc())\
                   .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': logs.page,
            'per_page': logs.per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener logs de auditoría'}), 500

@auditoria_api.route('/auditoria/logs/usuario/<int:usuario_id>', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_logs_usuario(current_user, usuario_id):
    """Obtener logs de un usuario específico"""
    try:
        limite = request.args.get('limit', 50, type=int)
        logs = AuditoriaLog.obtener_logs_usuario(usuario_id, limite)
        
        return jsonify([log.to_dict() for log in logs]), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener logs del usuario'}), 500

@auditoria_api.route('/auditoria/logs/tabla/<tabla>', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_logs_tabla(current_user, tabla):
    """Obtener logs de una tabla específica"""
    try:
        limite = request.args.get('limit', 50, type=int)
        logs = AuditoriaLog.obtener_logs_tabla(tabla, limite)
        
        return jsonify([log.to_dict() for log in logs]), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener logs de la tabla'}), 500

@auditoria_api.route('/auditoria/logs/registro/<tabla>/<registro_id>', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_logs_registro(current_user, tabla, registro_id):
    """Obtener historial de cambios de un registro específico"""
    try:
        limite = request.args.get('limit', 20, type=int)
        logs = AuditoriaLog.query.filter(
            AuditoriaLog.tabla_afectada == tabla,
            AuditoriaLog.registro_id == registro_id
        ).order_by(AuditoriaLog.created_at.desc()).limit(limite).all()
        
        return jsonify([log.to_dict() for log in logs]), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener historial del registro'}), 500

@auditoria_api.route('/auditoria/reporte', methods=['GET'])
@token_required
@rol_requerido('admin')
def generar_reporte_auditoria(current_user):
    """Generar reporte de auditoría"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        usuario_id = request.args.get('usuario_id', type=int)
        accion = request.args.get('accion')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'message': 'Fechas de inicio y fin requeridas'}), 400
        
        fecha_inicio = datetime.fromisoformat(fecha_inicio)
        fecha_fin = datetime.fromisoformat(fecha_fin)
        
        query = AuditoriaLog.query.filter(
            AuditoriaLog.created_at >= fecha_inicio,
            AuditoriaLog.created_at <= fecha_fin
        )
        
        if usuario_id:
            query = query.filter(AuditoriaLog.usuario_id == usuario_id)
        if accion:
            query = query.filter(AuditoriaLog.accion == accion)
        
        logs = query.order_by(AuditoriaLog.created_at.desc()).all()
        
        # Estadísticas del reporte
        estadisticas = {
            'total_acciones': len(logs),
            'acciones_por_tipo': {},
            'usuarios_activos': set(),
            'tablas_afectadas': set()
        }
        
        for log in logs:
            estadisticas['acciones_por_tipo'][log.accion] = estadisticas['acciones_por_tipo'].get(log.accion, 0) + 1
            estadisticas['usuarios_activos'].add(log.usuario_id)
            estadisticas['tablas_afectadas'].add(log.tabla_afectada)
        
        estadisticas['usuarios_activos'] = len(estadisticas['usuarios_activos'])
        estadisticas['tablas_afectadas'] = len(estadisticas['tablas_afectadas'])
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'estadisticas': estadisticas,
            'periodo': {
                'inicio': fecha_inicio.isoformat(),
                'fin': fecha_fin.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al generar reporte'}), 500

@auditoria_api.route('/auditoria/estadisticas', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_estadisticas_auditoria(current_user):
    """Obtener estadísticas de auditoría"""
    try:
        # Últimas 24 horas
        hace_24h = datetime.utcnow() - timedelta(hours=24)
        hace_7d = datetime.utcnow() - timedelta(days=7)
        hace_30d = datetime.utcnow() - timedelta(days=30)
        
        estadisticas = {
            'ultimas_24h': AuditoriaLog.query.filter(AuditoriaLog.created_at >= hace_24h).count(),
            'ultimos_7dias': AuditoriaLog.query.filter(AuditoriaLog.created_at >= hace_7d).count(),
            'ultimos_30dias': AuditoriaLog.query.filter(AuditoriaLog.created_at >= hace_30d).count(),
            'total_logs': AuditoriaLog.query.count(),
            'acciones_mas_comunes': {},
            'usuarios_mas_activos': {}
        }
        
        # Acciones más comunes en los últimos 7 días
        logs_7d = AuditoriaLog.query.filter(AuditoriaLog.created_at >= hace_7d).all()
        for log in logs_7d:
            estadisticas['acciones_mas_comunes'][log.accion] = estadisticas['acciones_mas_comunes'].get(log.accion, 0) + 1
        
        # Usuarios más activos en los últimos 7 días
        for log in logs_7d:
            if log.usuario:
                nombre = log.usuario.nombre
                estadisticas['usuarios_mas_activos'][nombre] = estadisticas['usuarios_mas_activos'].get(nombre, 0) + 1
        
        # Ordenar por frecuencia
        estadisticas['acciones_mas_comunes'] = dict(
            sorted(estadisticas['acciones_mas_comunes'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        estadisticas['usuarios_mas_activos'] = dict(
            sorted(estadisticas['usuarios_mas_activos'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return jsonify(estadisticas), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener estadísticas'}), 500

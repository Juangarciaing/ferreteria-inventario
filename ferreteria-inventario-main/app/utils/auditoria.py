"""
Utilidades para auditoría y logging
"""
from functools import wraps
from flask import request, current_app, g
from app.models.auditoria import AuditoriaLog
import json

def auditar_accion(accion, tabla_afectada):
    """Decorador para auditar acciones automáticamente"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener usuario actual si está disponible
            usuario_id = getattr(g, 'current_user', None)
            if hasattr(usuario_id, 'id'):
                usuario_id = usuario_id.id
            
            # Obtener datos de la request
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            user_agent = request.environ.get('HTTP_USER_AGENT')
            
            # Ejecutar la función original
            result = f(*args, **kwargs)
            
            # Registrar en auditoría si hay usuario
            if usuario_id:
                try:
                    AuditoriaLog.registrar_accion(
                        usuario_id=usuario_id,
                        accion=accion,
                        tabla_afectada=tabla_afectada,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        detalles_adicionales=f"Endpoint: {request.endpoint}, Método: {request.method}"
                    )
                except Exception as e:
                    current_app.logger.error(f"Error al registrar auditoría: {e}")
            
            return result
        return decorated_function
    return decorator

def auditar_cambio_registro(usuario_id, accion, tabla_afectada, registro_id, 
                           datos_anteriores=None, datos_nuevos=None):
    """Registrar cambios específicos en un registro"""
    try:
        return AuditoriaLog.registrar_accion(
            usuario_id=usuario_id,
            accion=accion,
            tabla_afectada=tabla_afectada,
            registro_id=registro_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR')),
            user_agent=request.environ.get('HTTP_USER_AGENT')
        )
    except Exception as e:
        current_app.logger.error(f"Error al registrar cambio: {e}")
        return None

def obtener_cambios_registro(tabla_afectada, registro_id, limite=20):
    """Obtener historial de cambios de un registro específico"""
    try:
        return AuditoriaLog.query.filter(
            AuditoriaLog.tabla_afectada == tabla_afectada,
            AuditoriaLog.registro_id == str(registro_id)
        ).order_by(AuditoriaLog.created_at.desc()).limit(limite).all()
    except Exception as e:
        current_app.logger.error(f"Error al obtener cambios: {e}")
        return []

def generar_reporte_auditoria(fecha_inicio, fecha_fin, usuario_id=None, accion=None):
    """Generar reporte de auditoría para un período"""
    try:
        query = AuditoriaLog.query.filter(
            AuditoriaLog.created_at >= fecha_inicio,
            AuditoriaLog.created_at <= fecha_fin
        )
        
        if usuario_id:
            query = query.filter(AuditoriaLog.usuario_id == usuario_id)
        
        if accion:
            query = query.filter(AuditoriaLog.accion == accion)
        
        return query.order_by(AuditoriaLog.created_at.desc()).all()
    except Exception as e:
        current_app.logger.error(f"Error al generar reporte: {e}")
        return []

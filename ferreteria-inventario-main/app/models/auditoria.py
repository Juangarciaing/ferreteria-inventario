"""
Modelo de Auditoría para registrar todas las acciones críticas
"""
from app import db
from .base import BaseModel
from datetime import datetime

class AuditoriaLog(BaseModel):
    """Modelo para registrar logs de auditoría"""
    __tablename__ = 'auditoria_logs'
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(100), nullable=False)  # 'crear_producto', 'actualizar_precio', etc.
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.String(50), nullable=True)
    datos_anteriores = db.Column(db.JSON, nullable=True)
    datos_nuevos = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    detalles_adicionales = db.Column(db.Text, nullable=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='auditoria_logs')
    
    def to_dict(self):
        """Convertir a diccionario"""
        data = super().to_dict()
        if self.usuario:
            data['usuario'] = {
                'id': self.usuario.id,
                'nombre': self.usuario.nombre,
                'email': self.usuario.email
            }
        return data
    
    @classmethod
    def registrar_accion(cls, usuario_id, accion, tabla_afectada, registro_id=None, 
                         datos_anteriores=None, datos_nuevos=None, ip_address=None, 
                         user_agent=None, detalles_adicionales=None):
        """Registrar una acción en el log de auditoría"""
        try:
            log = cls(
                usuario_id=usuario_id,
                accion=accion,
                tabla_afectada=tabla_afectada,
                registro_id=str(registro_id) if registro_id else None,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=ip_address,
                user_agent=user_agent,
                detalles_adicionales=detalles_adicionales
            )
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar auditoría: {e}")
            return None
    
    @classmethod
    def obtener_logs_usuario(cls, usuario_id, limite=50):
        """Obtener logs de un usuario específico"""
        return cls.query.filter_by(usuario_id=usuario_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limite).all()
    
    @classmethod
    def obtener_logs_tabla(cls, tabla_afectada, limite=50):
        """Obtener logs de una tabla específica"""
        return cls.query.filter_by(tabla_afectada=tabla_afectada)\
                       .order_by(cls.created_at.desc())\
                       .limit(limite).all()
    
    @classmethod
    def obtener_logs_accion(cls, accion, limite=50):
        """Obtener logs de una acción específica"""
        return cls.query.filter_by(accion=accion)\
                       .order_by(cls.created_at.desc())\
                       .limit(limite).all()

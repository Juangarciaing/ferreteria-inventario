"""
Modelo de Usuario
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from .base import BaseModel

class Usuario(BaseModel, UserMixin):
    """Modelo de usuario del sistema"""
    __tablename__ = 'usuarios'
    
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    # Usar 'password' para coincidir con la columna real en MySQL
    password = db.Column(db.String(255), nullable=False)
    # En la BD es enum('admin','vendedor'); usamos string con default compatible
    rol = db.Column(db.String(20), nullable=False, default='vendedor')
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    # Campo activo (mapeado desde la columna 'activo' en MySQL como TINYINT(1))
    # Usar Integer en lugar de Boolean para compatibilidad con MySQL TINYINT
    activo = db.Column(db.Integer, nullable=False, default=1)

    # Relaciones
    ventas = db.relationship('Venta', back_populates='usuario', cascade='all, delete-orphan')
    compras = db.relationship('Compra', back_populates='usuario', cascade='all, delete-orphan')

    def set_password(self, password):
        """Establecer contraseña encriptada"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """Convertir a diccionario sin contraseña"""
        data = super().to_dict()
        data.pop('password', None)
        # Convertir activo (TINYINT) a boolean para el frontend
        data['estado'] = bool(self.activo)
        return data
    
    @classmethod
    def find_by_email(cls, email):
        """Buscar usuario por email"""
        return cls.query.filter_by(email=email).first()
    
    def is_admin(self):
        """Verificar si el usuario es administrador"""
        return self.rol == 'admin'
    
    def is_active_user(self):
        """Comprueba si el usuario está activo."""
        return bool(self.activo)
"""
Modelo de Proveedor
"""
from app import db
from .base import BaseModel

class Proveedor(BaseModel):
    """Modelo de proveedor de productos"""
    __tablename__ = 'proveedores'
    
    nombre = db.Column(db.String(200), nullable=False)
    contacto = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    rut_ruc = db.Column(db.String(50))
    condiciones_pago = db.Column(db.String(20), default='contado')  # contado, credito_30, credito_60
    descuento_default = db.Column(db.Numeric(5, 2), default=0.0)
    estado = db.Column(db.String(20), default='activo')  # activo, inactivo
    rating = db.Column(db.Numeric(2, 1), default=0.0)  # 1.0 - 5.0 estrellas
    notas = db.Column(db.Text)
    
    # Relaciones
    compras = db.relationship('Compra', back_populates='proveedor', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertir a diccionario"""
        data = super().to_dict()
        return data
    
    @classmethod
    def get_active_providers(cls):
        """Obtener proveedores activos"""
        return cls.query.filter_by(estado='activo').all()
    
    @classmethod
    def find_by_name(cls, nombre):
        """Buscar proveedor por nombre"""
        return cls.query.filter_by(nombre=nombre).first()
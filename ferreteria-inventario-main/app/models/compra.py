"""
Modelo de Compra
"""
from app import db
from sqlalchemy import func
from .base import BaseModel

class Compra(BaseModel):
    """Modelo de compra de productos para stock"""
    __tablename__ = 'compras'
    
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_compra = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relaciones
    producto = db.relationship('Producto', back_populates='compras')
    usuario = db.relationship('Usuario', back_populates='compras')
    proveedor = db.relationship('Proveedor', back_populates='compras')
    
    def to_dict(self):
        """Convertir a diccionario incluyendo producto, usuario y proveedor"""
        data = super().to_dict()
        if self.producto:
            data['producto'] = self.producto.to_dict()
        if self.usuario:
            data['usuario'] = {
                'id': self.usuario.id,
                'nombre': self.usuario.nombre,
                'email': self.usuario.email
            }
        if self.proveedor:
            data['proveedor'] = self.proveedor.to_dict()
        return data
    
    @classmethod
    def get_purchases_by_date_range(cls, fecha_inicio, fecha_fin):
        """Obtener compras en rango de fechas"""
        return cls.query.filter(
            cls.created_at >= fecha_inicio,
            cls.created_at <= fecha_fin
        ).all()
    
    @classmethod
    def get_total_purchases(cls, fecha_inicio=None, fecha_fin=None):
        """Obtener total de compras"""
        query = db.session.query(func.sum(cls.total))
        if fecha_inicio and fecha_fin:
            query = query.filter(
                cls.created_at >= fecha_inicio,
                cls.created_at <= fecha_fin
            )
        result = query.scalar()
        return float(result) if result else 0.0
    
    def calculate_total(self):
        """Calcular total automáticamente"""
        self.total = self.cantidad * self.precio_unitario
        return self.total
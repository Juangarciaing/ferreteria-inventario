"""
Modelos de Venta y DetalleVenta
"""
from app import db
from sqlalchemy import func
from .base import BaseModel

class Venta(BaseModel):
    """Modelo de venta"""
    __tablename__ = 'ventas'
    
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Numeric(10, 2), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Información opcional del cliente
    cliente_nombre = db.Column(db.String(200), nullable=True)
    cliente_documento = db.Column(db.String(50), nullable=True)
    cliente_telefono = db.Column(db.String(20), nullable=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', back_populates='ventas')
    detalles = db.relationship('DetalleVenta', back_populates='venta', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertir a diccionario incluyendo detalles"""
        data = super().to_dict()
        if self.usuario:
            data['usuario'] = self.usuario.to_dict()
        if self.detalles:
            data['detalles'] = [detalle.to_dict() for detalle in self.detalles]
        return data
    
    @classmethod
    def get_sales_by_date_range(cls, fecha_inicio, fecha_fin):
        """Obtener ventas en rango de fechas"""
        return cls.query.filter(
            cls.created_at >= fecha_inicio,
            cls.created_at <= fecha_fin
        ).all()
    
    @classmethod
    def get_total_sales(cls, fecha_inicio=None, fecha_fin=None):
        """Obtener total de ventas"""
        query = db.session.query(func.sum(cls.total))
        if fecha_inicio and fecha_fin:
            query = query.filter(
                cls.created_at >= fecha_inicio,
                cls.created_at <= fecha_fin
            )
        result = query.scalar()
        return float(result) if result else 0.0

class DetalleVenta(BaseModel):
    """Detalle de cada producto vendido en una venta"""
    __tablename__ = 'detalle_venta'
    
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relaciones
    venta = db.relationship('Venta', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalles')
    
    def to_dict(self):
        """Convertir a diccionario incluyendo producto"""
        data = super().to_dict()
        if self.producto:
            data['producto'] = self.producto.to_dict()
        return data
    
    def calculate_subtotal(self):
        """Calcular subtotal automáticamente"""
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal
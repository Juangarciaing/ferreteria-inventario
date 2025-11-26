"""
Modelo de Producto y Categoria
"""
from app import db
from .base import BaseModel

# Constante para cascada de eliminación
CASCADE_DELETE_ORPHAN = 'all, delete-orphan'

class Categoria(BaseModel):
    """Modelo de categoría de productos"""
    __tablename__ = 'categorias'
    
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    
    # Relaciones
    productos = db.relationship('Producto', back_populates='categoria', cascade=CASCADE_DELETE_ORPHAN)
    
    def to_dict(self):
        """Convertir a diccionario"""
        return super().to_dict()
    
    @classmethod
    def find_by_name(cls, nombre):
        """Buscar categoría por nombre"""
        return cls.query.filter_by(nombre=nombre).first()

class Producto(BaseModel):
    """Modelo de producto"""
    __tablename__ = 'productos'
    
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    descripcion = db.Column(db.Text)
    codigo_barras = db.Column(db.String(13), unique=True, nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    
    # Relaciones
    categoria = db.relationship('Categoria', back_populates='productos')
    proveedor = db.relationship('Proveedor', lazy='joined', foreign_keys=[proveedor_id])
    detalles = db.relationship('DetalleVenta', back_populates='producto', cascade=CASCADE_DELETE_ORPHAN)
    compras = db.relationship('Compra', back_populates='producto', cascade=CASCADE_DELETE_ORPHAN)
    
    def to_dict(self):
        """Convertir a diccionario incluyendo categoria"""
        data = super().to_dict()
        if self.categoria:
            data['categoria'] = self.categoria.to_dict()
        return data
    
    @classmethod
    def get_low_stock(cls, limit=None):
        """Obtener productos con stock bajo"""
        query = cls.query.filter(cls.stock <= cls.stock_minimo)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def search_by_name(cls, nombre):
        """Buscar productos por nombre"""
        return cls.query.filter(cls.nombre.like(f'%{nombre}%')).all()
    
    @classmethod
    def find_by_barcode(cls, codigo_barras):
        """Buscar producto por código de barras"""
        return cls.query.filter_by(codigo_barras=codigo_barras).first()
    
    def has_sufficient_stock(self, cantidad):
        """Verificar si hay suficiente stock"""
        return self.stock >= cantidad
    
    def update_stock(self, cantidad, operation='add'):
        """Actualizar stock del producto"""
        if operation == 'add':
            self.stock += cantidad
        elif operation == 'subtract':
            if self.stock >= cantidad:
                self.stock -= cantidad
            else:
                raise ValueError("Stock insuficiente")
        else:
            raise ValueError("Operación debe ser 'add' o 'subtract'")
        
        self.save()
        return self
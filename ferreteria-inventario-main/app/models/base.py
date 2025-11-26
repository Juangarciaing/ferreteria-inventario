"""
Modelo base de la aplicación
"""
from app import db

class BaseModel(db.Model):
    """Modelo base con campos comunes"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime, 
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
    
    def to_dict(self):
        """Convertir modelo a diccionario"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if value is not None:
                # Convertir datetime a string ISO
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                # Convertir Decimal a float
                elif hasattr(value, '__float__'):
                    value = float(value)
            result[column.name] = value
        return result
    
    def save(self):
        """Guardar el modelo en la base de datos"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Eliminar el modelo de la base de datos"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Obtener modelo por ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Obtener todos los registros"""
        return cls.query.all()
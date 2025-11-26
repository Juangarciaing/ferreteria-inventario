"""
Repositorio base - Implementación genérica de operaciones CRUD
Infrastructure Layer

Principios aplicados:
- DRY: No repetir código CRUD en cada repositorio
- Template Method: Define algoritmo base que subclases pueden usar
- Single Responsibility: Solo maneja operaciones de persistencia
"""
from abc import ABC
from typing import List, Optional, TypeVar, Generic
from app import db
from app.exceptions import NotFoundError, DatabaseError

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Repositorio base con operaciones CRUD genéricas.
    Las subclases deben definir el atributo 'model'.
    
    Uso:
        class ProveedorRepository(BaseRepository):
            model = Proveedor
    """
    
    model = None  # Debe ser definido en subclases
    
    @classmethod
    def get_by_id(cls, entity_id: int) -> Optional[T]:
        """
        Obtener entidad por ID
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Entidad o None si no existe
        """
        try:
            return cls.model.query.get(entity_id)
        except Exception as e:
            raise DatabaseError(f"Error al buscar {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def get_all(cls) -> List[T]:
        """Obtener todas las entidades"""
        try:
            return cls.model.query.all()
        except Exception as e:
            raise DatabaseError(f"Error al obtener {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def create(cls, data: dict) -> T:
        """
        Crear nueva entidad
        
        Args:
            data: Diccionario con datos de la entidad
            
        Returns:
            Entidad creada
        """
        try:
            # Remover campos que no existen en el modelo
            valid_data = {k: v for k, v in data.items() if hasattr(cls.model, k)}
            instance = cls.model(**valid_data)
            db.session.add(instance)
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def update(cls, entity_id: int, data: dict) -> T:
        """
        Actualizar entidad existente
        
        Args:
            entity_id: ID de la entidad
            data: Diccionario con campos a actualizar
            
        Returns:
            Entidad actualizada
        """
        try:
            instance = cls.get_by_id(entity_id)
            if not instance:
                raise NotFoundError(f"{cls.model.__name__} con ID {entity_id} no encontrado")
            
            print(f"\n{'='*80}")
            print(f"[BASE_REPOSITORY_UPDATE] Actualizando {cls.model.__name__} ID: {entity_id}")
            print(f"[DEBUG] 📦 Datos a actualizar: {data}")
            
            # Actualizar solo campos que existen en el modelo
            for key, value in data.items():
                print(f"[DEBUG] 🔍 Procesando campo '{key}' = {value} (tipo: {type(value).__name__})")
                
                if hasattr(instance, key):
                    print(f"[DEBUG] ✅ El modelo tiene el atributo '{key}'")
                    
                    # CRÍTICO: Permitir valores 0 y False
                    if value is not None:
                        valor_anterior = getattr(instance, key)
                        print(f"[DEBUG] 🔄 Cambiando '{key}': {valor_anterior} → {value}")
                        setattr(instance, key, value)
                        print(f"[DEBUG] ✅ Valor actualizado en instancia")
                    else:
                        print(f"[DEBUG] ⚠️  Valor es None, ignorando campo '{key}'")
                else:
                    print(f"[DEBUG] ❌ El modelo NO tiene el atributo '{key}'")
            
            print(f"[DEBUG] 🚀 Ejecutando db.session.commit()...")
            db.session.commit()
            print(f"[DEBUG] ✅ COMMIT EXITOSO")
            print(f"{'='*80}\n")
            
            return instance
        except NotFoundError:
            raise
        except Exception as e:
            print(f"[DEBUG] ❌ ERROR en update: {str(e)}")
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def delete(cls, entity_id: int) -> bool:
        """
        Eliminar entidad
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            instance = cls.get_by_id(entity_id)
            if not instance:
                raise NotFoundError(f"{cls.model.__name__} con ID {entity_id} no encontrado")
            
            db.session.delete(instance)
            db.session.commit()
            return True
        except NotFoundError:
            raise
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error al eliminar {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def exists(cls, entity_id: int) -> bool:
        """
        Verificar si existe una entidad
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            True si existe
        """
        try:
            return cls.model.query.filter_by(id=entity_id).first() is not None
        except Exception as e:
            raise DatabaseError(f"Error al verificar {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def count(cls) -> int:
        """Contar entidades"""
        try:
            return cls.model.query.count()
        except Exception as e:
            raise DatabaseError(f"Error al contar {cls.model.__name__}: {str(e)}")

"""
DTO Base y utilidades de validación
Principio: DRY (Don't Repeat Yourself)
"""
from typing import Dict, Any, List
from dataclasses import dataclass

class ValidationError(Exception):
    """Excepción personalizada para errores de validación de DTOs"""
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(f"Errores de validación: {errors}")

@dataclass
class BaseDTO:
    """
    DTO base con métodos comunes de validación.
    Todos los DTOs heredan de esta clase.
    """
    
    def validate(self) -> None:
        """
        Valida el DTO y lanza ValidationError si hay errores.
        Debe ser implementado por las clases hijas.
        """
        errors = self._get_validation_errors()
        if errors:
            raise ValidationError(errors)
    
    def _get_validation_errors(self) -> Dict[str, List[str]]:
        """
        Obtiene diccionario de errores de validación.
        Debe ser sobreescrito por clases hijas.
        
        Returns:
            Dict con campo como key y lista de errores como value
        """
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a diccionario"""
        return {
            key: value for key, value in self.__dict__.items() 
            if value is not None and not key.startswith('_')
        }
    
    @staticmethod
    def _validate_required(value: Any, field_name: str, errors: Dict[str, List[str]]) -> None:
        """Helper para validar campos requeridos"""
        if value is None or (isinstance(value, str) and not value.strip()):
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(f"{field_name} es requerido")
    
    @staticmethod
    def _validate_email(email: str, field_name: str, errors: Dict[str, List[str]]) -> None:
        """Helper para validar formato de email"""
        import re
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(f"{field_name} no tiene formato válido")
    
    @staticmethod
    def _validate_min_length(value: str, min_len: int, field_name: str, errors: Dict[str, List[str]]) -> None:
        """Helper para validar longitud mínima"""
        if value and len(value) < min_len:
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(f"{field_name} debe tener al menos {min_len} caracteres")
    
    @staticmethod
    def _validate_max_length(value: str, max_len: int, field_name: str, errors: Dict[str, List[str]]) -> None:
        """Helper para validar longitud máxima"""
        if value and len(value) > max_len:
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(f"{field_name} no puede exceder {max_len} caracteres")
    
    @staticmethod
    def _validate_positive(value: float, field_name: str, errors: Dict[str, List[str]]) -> None:
        """Helper para validar números positivos"""
        if value is not None and value < 0:
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(f"{field_name} debe ser un número positivo")

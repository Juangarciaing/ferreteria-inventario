"""
Use Cases para Usuario
Contienen la lógica de negocio para las operaciones de usuarios y autenticación

Principios aplicados:
- Single Responsibility: Cada use case tiene una única responsabilidad
- Dependency Inversion: Dependen de interfaces, no de implementaciones
- Security: Manejo seguro de contraseñas y autenticación
"""
from typing import List, Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from app.domain.interfaces.usuario_repository_interface import IUsuarioRepository
from app.application.dtos.usuario_dto import (
    CreateUsuarioDTO, UpdateUsuarioDTO, ChangePasswordDTO,
    LoginDTO, UsuarioResponseDTO
)
from app.exceptions import NotFoundError, ValidationError, BusinessLogicError


class CreateUsuarioUseCase:
    """
    Caso de uso: Crear un nuevo usuario
    
    Proceso:
    1. Validar datos de entrada
    2. Verificar que el email no exista
    3. Hashear la contraseña
    4. Crear el usuario
    5. Retornar DTO de respuesta (sin password)
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, data: Dict) -> Dict:
        """
        Ejecuta la creación de un usuario
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            Diccionario con los datos del usuario creado (sin password)
            
        Raises:
            ValidationError: Si los datos son inválidos o el email ya existe
        """
        # 1. Validar datos
        dto = CreateUsuarioDTO(**data)
        errors = dto.validate()
        if errors:
            raise ValidationError("Datos de usuario inválidos", errors)
        
        # 2. Verificar que el email no exista
        if self.usuario_repository.email_exists(dto.email):
            raise ValidationError("El email ya está registrado", {'email': 'Este email ya está en uso'})
        
        # 3. Preparar datos con password hasheada
        usuario_data = {
            'nombre': dto.nombre,
            'email': dto.email.lower(),  # Normalizar email a minúsculas
            'password': generate_password_hash(dto.password),  # Hashear password
            'rol': dto.rol,
            'telefono': dto.telefono,
            'direccion': dto.direccion,
            'activo': 1  # Nuevo usuario activo por defecto
        }
        
        # 4. Crear el usuario
        usuario = self.usuario_repository.create(**usuario_data)
        
        # 5. Retornar DTO de respuesta (sin password)
        return UsuarioResponseDTO.from_entity(usuario).to_dict()


class UpdateUsuarioUseCase:
    """Caso de uso: Actualizar un usuario existente"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, usuario_id: int, data: Dict) -> Dict:
        """
        Actualiza un usuario
        
        Args:
            usuario_id: ID del usuario a actualizar
            data: Diccionario con los datos a actualizar
            
        Returns:
            Diccionario con los datos del usuario actualizado
            
        Raises:
            NotFoundError: Si el usuario no existe
            ValidationError: Si los datos son inválidos o el email ya existe
        """
        print(f"\n{'='*80}")
        print(f"[USE_CASE_UPDATE] Iniciando actualización de usuario ID: {usuario_id}")
        print(f"[DEBUG] 📦 Datos recibidos: {data}")
        
        # Verificar que el usuario existe
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        print(f"[DEBUG] ✅ Usuario encontrado: {usuario.nombre}")
        
        # Validar datos
        dto = UpdateUsuarioDTO(**data)
        errors = dto.validate()
        if errors:
            raise ValidationError("Datos de actualización inválidos", errors)
        
        print(f"[DEBUG] ✅ Validación exitosa")
        
        # Verificar email único si se está actualizando
        if dto.email and self.usuario_repository.email_exists(dto.email, exclude_id=usuario_id):
            raise ValidationError("El email ya está registrado", {'email': 'Este email ya está en uso'})
        
        # Preparar datos para actualizar (solo los proporcionados)
        update_data = {}
        if dto.nombre is not None:
            update_data['nombre'] = dto.nombre
        if dto.email is not None:
            update_data['email'] = dto.email.lower()
        if dto.rol is not None:
            update_data['rol'] = dto.rol
        if dto.telefono is not None:
            update_data['telefono'] = dto.telefono
        if dto.direccion is not None:
            update_data['direccion'] = dto.direccion
        if dto.activo is not None:
            print(f"[DEBUG] 🔄 Campo 'activo' será actualizado: {dto.activo}")
            update_data['activo'] = dto.activo
        
        print(f"[DEBUG] 📦 Datos preparados para repositorio: {update_data}")
        
        # Actualizar
        usuario_actualizado = self.usuario_repository.update(usuario_id, update_data)
        
        print(f"[DEBUG] ✅ Actualización completada en use case")
        print(f"{'='*80}\n")
        
        return UsuarioResponseDTO.from_entity(usuario_actualizado).to_dict()


class DeleteUsuarioUseCase:
    """Caso de uso: Eliminar (desactivar) un usuario"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, usuario_id: int) -> bool:
        """
        Elimina (desactiva) un usuario
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si el usuario no existe
        """
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        return self.usuario_repository.delete(usuario_id)


class GetUsuarioUseCase:
    """Caso de uso: Obtener un usuario por ID"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, usuario_id: int) -> Dict:
        """
        Obtiene un usuario por su ID
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con los datos del usuario (sin password)
            
        Raises:
            NotFoundError: Si el usuario no existe
        """
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        return UsuarioResponseDTO.from_entity(usuario).to_dict()


class GetAllUsuariosUseCase:
    """Caso de uso: Obtener todos los usuarios"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, only_active: bool = False) -> List[Dict]:
        """
        Obtiene todos los usuarios
        
        Args:
            only_active: Si es True, solo retorna usuarios activos
            
        Returns:
            Lista de diccionarios con los usuarios (sin passwords)
        """
        if only_active:
            usuarios = self.usuario_repository.get_active_users()
        else:
            usuarios = self.usuario_repository.get_all()
        
        return [UsuarioResponseDTO.from_entity(u).to_dict() for u in usuarios]


class GetUsuariosByRolUseCase:
    """Caso de uso: Obtener usuarios por rol"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, rol: str) -> List[Dict]:
        """
        Obtiene usuarios por rol
        
        Args:
            rol: Rol a filtrar ('admin' o 'vendedor')
            
        Returns:
            Lista de diccionarios con los usuarios
            
        Raises:
            ValidationError: Si el rol no es válido
        """
        if rol not in ['admin', 'vendedor']:
            raise ValidationError("Rol inválido", {'rol': 'El rol debe ser "admin" o "vendedor"'})
        
        usuarios = self.usuario_repository.get_by_rol(rol)
        return [UsuarioResponseDTO.from_entity(u).to_dict() for u in usuarios]


class SearchUsuariosUseCase:
    """Caso de uso: Buscar usuarios"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, query: str) -> List[Dict]:
        """
        Busca usuarios por nombre o email
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de diccionarios con los usuarios encontrados
        """
        if not query or len(query.strip()) < 2:
            return []
        
        usuarios = self.usuario_repository.search(query)
        return [UsuarioResponseDTO.from_entity(u).to_dict() for u in usuarios]


class LoginUseCase:
    """
    Caso de uso: Autenticar un usuario
    
    Proceso:
    1. Validar datos de entrada
    2. Buscar usuario por email
    3. Verificar que el usuario existe y está activo
    4. Verificar la contraseña
    5. Retornar datos del usuario (sin password)
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, data: Dict) -> Dict:
        """
        Autentica un usuario
        
        Args:
            data: Diccionario con email y password
            
        Returns:
            Diccionario con los datos del usuario autenticado
            
        Raises:
            ValidationError: Si los datos son inválidos
            BusinessLogicError: Si las credenciales son incorrectas o el usuario está inactivo
        """
        # 1. Validar datos
        dto = LoginDTO(**data)
        errors = dto.validate()
        if errors:
            raise ValidationError("Datos de login inválidos", errors)
        
        # 2. Buscar usuario por email
        usuario = self.usuario_repository.get_by_email(dto.email.lower())
        
        # 3. Verificar que el usuario existe
        if not usuario:
            raise BusinessLogicError("Credenciales incorrectas")
        
        # 4. Verificar que el usuario está activo
        if not usuario.is_active_user():
            raise BusinessLogicError("Usuario inactivo")
        
        # 5. Verificar la contraseña
        if not check_password_hash(usuario.password, dto.password):
            raise BusinessLogicError("Credenciales incorrectas")
        
        # 6. Retornar datos del usuario (sin password)
        return UsuarioResponseDTO.from_entity(usuario).to_dict()


class ChangePasswordUseCase:
    """Caso de uso: Cambiar la contraseña de un usuario"""
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository
    
    def execute(self, usuario_id: int, data: Dict) -> Dict:
        """
        Cambia la contraseña de un usuario
        
        Args:
            usuario_id: ID del usuario
            data: Diccionario con current_password y new_password
            
        Returns:
            Diccionario con mensaje de éxito
            
        Raises:
            NotFoundError: Si el usuario no existe
            ValidationError: Si los datos son inválidos
            BusinessLogicError: Si la contraseña actual es incorrecta
        """
        # Verificar que el usuario existe
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        # Validar datos
        dto = ChangePasswordDTO(**data)
        errors = dto.validate()
        if errors:
            raise ValidationError("Datos de cambio de contraseña inválidos", errors)
        
        # Verificar contraseña actual
        if not check_password_hash(usuario.password, dto.current_password):
            raise BusinessLogicError("La contraseña actual es incorrecta")
        
        # Actualizar contraseña
        self.usuario_repository.update(usuario_id, {
            'password': generate_password_hash(dto.new_password)
        })
        
        return {'message': 'Contraseña actualizada exitosamente'}

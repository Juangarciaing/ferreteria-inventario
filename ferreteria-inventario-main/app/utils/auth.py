"""
Utilidades para autenticación JWT
"""
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import request, jsonify, current_app
from app.exceptions import UnauthorizedError, ForbiddenError

class JWTManager:
    """Gestor de tokens JWT"""
    
    @staticmethod
    def generate_token(user_id, rol):
        """Generar token JWT"""
        payload = {
            'user_id': user_id,
            'rol': rol,
            'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def decode_token(token):
        """Decodificar token JWT"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token expirado')
        except jwt.InvalidTokenError:
            raise UnauthorizedError('Token inválido')

def token_required(f):
    """Decorador para requerir token JWT válido"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                raise UnauthorizedError('Formato de token inválido')
        
        if not token:
            raise UnauthorizedError('Token requerido')
        
        try:
            payload = JWTManager.decode_token(token)
            current_user_data = {
                'id': payload['user_id'],
                'rol': payload['rol']
            }
            return f(current_user_data, *args, **kwargs)
        except Exception as e:
            if isinstance(e, (UnauthorizedError, ForbiddenError)):
                raise
            raise UnauthorizedError('Token inválido')
    
    return decorated

def rol_requerido(*roles):
    """Decorador para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user['rol'] not in roles:
                raise ForbiddenError('Acceso no autorizado para este rol')
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator
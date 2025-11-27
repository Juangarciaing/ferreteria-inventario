import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import config

db = SQLAlchemy()

def create_app(config_name=None):
    """Crea y configura la aplicación Flask con arquitectura limpia."""
    app = Flask(__name__)
    
    # Configuración
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Inicializar cache y rate limiter
    from .extensions import cache, limiter
    cache.init_app(app)
    limiter.init_app(app)
    
    # Configurar CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # ===== CONFIGURAR LOGGING =====
    from .utils.logger import setup_logger
    setup_logger(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Inicializar Swagger para documentación (opcional)
    if app.config.get('ENABLE_API_DOCS', True):
        try:
            from .api_docs import init_swagger
            init_swagger(app)
        except ImportError:
            # flasgger no instalado; continuar sin docs
            pass
    
    # Registrar manejadores de errores
    register_error_handlers(app)

    # Importar modelos para SQLAlchemy (asegurar que se registren)
    from app.models import Usuario, Producto, Categoria, Venta, DetalleVenta, Compra, Proveedor
    from app.models.auditoria import AuditoriaLog

    return app

def register_blueprints(app):
    """Registrar todos los blueprints"""    
    # Ruta raíz básica
    @app.route('/')
    def home():
        from flask import jsonify
        return jsonify({
            'message': 'Sistema de Inventario Ferretería - API',
            'version': '1.0',
            'status': 'funcionando',
            'frontend': 'http://localhost:3000',
            'api_docs': '/api'
        })
    
    # === Clean Architecture Controllers (register FIRST to take precedence) ===
    from .controllers.usuario import usuario_bp
    app.register_blueprint(usuario_bp)
    
    from .controllers.producto import producto_bp
    app.register_blueprint(producto_bp)
    
    from .controllers.categoria import categoria_bp
    app.register_blueprint(categoria_bp)
    
    from .controllers.proveedor import proveedor_bp
    app.register_blueprint(proveedor_bp)
    
    from .controllers.venta import venta_bp
    app.register_blueprint(venta_bp)
    
    from .controllers.compra import compra_bp
    app.register_blueprint(compra_bp)
    
    # API Blueprint principal (legacy routes, registered after for backward compatibility)
    from .api_routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    # API adicional con nuevos endpoints
    from .api_additional import additional_api
    app.register_blueprint(additional_api, url_prefix='/api')
    
    # API de auditoría
    from .api_auditoria import auditoria_api
    app.register_blueprint(auditoria_api, url_prefix='/api')
    
    # API de exportación
    from .api_export import export_api
    app.register_blueprint(export_api, url_prefix='/api')
    
    # API de documentación (opcional)
    try:
        from .api_docs import docs_bp
        app.register_blueprint(docs_bp)
    except ImportError:
        # flasgger/api_docs no disponible; omitir docs
        pass
    
    # API de monitoreo
    from .api_monitoring import monitoring_api
    app.register_blueprint(monitoring_api, url_prefix='/api')
    
    # API de backup
    from .api_backup import backup_api
    app.register_blueprint(backup_api, url_prefix='/api')
    
    # ===== API de Health Check =====
    from .api_health import health_bp
    app.register_blueprint(health_bp)

def register_error_handlers(app):
    """Registrar manejadores de errores globales"""
    from app.utils import handle_error, create_response
    from app.exceptions import BusinessLogicError, UnauthorizedError, ForbiddenError
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(error):
        return create_response(message=str(error), status_code=401)
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        return create_response(message=str(error), status_code=403)
    
    @app.errorhandler(BusinessLogicError)
    def handle_business_error(error):
        return handle_error(error)
    
    @app.errorhandler(404)
    def not_found(error):
        return create_response(message="Endpoint no encontrado", status_code=404)
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return create_response(message="Error interno del servidor", status_code=500)
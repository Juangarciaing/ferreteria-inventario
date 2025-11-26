"""
Documentación de API con Swagger
"""
from flask import Blueprint, jsonify
from flasgger import Swagger, swag_from
from app import create_app

# Crear blueprint para documentación
docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/api/docs')
def api_docs():
    """Documentación de la API"""
    return jsonify({
        'title': 'Sistema de Inventario Ferretería - API',
        'version': '1.0.0',
        'description': 'API REST para el sistema de gestión de inventario de ferretería',
        'endpoints': {
            'autenticacion': {
                'POST /api/auth/login': 'Iniciar sesión',
                'POST /api/auth/logout': 'Cerrar sesión',
                'GET /api/auth/me': 'Obtener información del usuario actual'
            },
            'productos': {
                'GET /api/productos': 'Obtener lista de productos',
                'POST /api/productos': 'Crear nuevo producto',
                'GET /api/productos/{id}': 'Obtener producto por ID',
                'PUT /api/productos/{id}': 'Actualizar producto',
                'DELETE /api/productos/{id}': 'Eliminar producto',
                'GET /api/productos/search': 'Buscar productos',
                'GET /api/productos/stock-bajo': 'Obtener productos con stock bajo'
            },
            'categorias': {
                'GET /api/categorias': 'Obtener lista de categorías',
                'POST /api/categorias': 'Crear nueva categoría',
                'GET /api/categorias/{id}': 'Obtener categoría por ID',
                'PUT /api/categorias/{id}': 'Actualizar categoría',
                'DELETE /api/categorias/{id}': 'Eliminar categoría'
            },
            'proveedores': {
                'GET /api/proveedores': 'Obtener lista de proveedores',
                'POST /api/proveedores': 'Crear nuevo proveedor',
                'GET /api/proveedores/{id}': 'Obtener proveedor por ID',
                'PUT /api/proveedores/{id}': 'Actualizar proveedor',
                'DELETE /api/proveedores/{id}': 'Eliminar proveedor'
            },
            'ventas': {
                'GET /api/ventas': 'Obtener lista de ventas',
                'POST /api/ventas': 'Crear nueva venta',
                'GET /api/ventas/{id}': 'Obtener venta por ID',
                'PUT /api/ventas/{id}': 'Actualizar venta',
                'DELETE /api/ventas/{id}': 'Eliminar venta'
            },
            'compras': {
                'GET /api/compras': 'Obtener lista de compras',
                'POST /api/compras': 'Crear nueva compra',
                'GET /api/compras/{id}': 'Obtener compra por ID',
                'PUT /api/compras/{id}': 'Actualizar compra',
                'DELETE /api/compras/{id}': 'Eliminar compra'
            },
            'usuarios': {
                'GET /api/usuarios': 'Obtener lista de usuarios (solo admin)',
                'POST /api/usuarios': 'Crear nuevo usuario (solo admin)',
                'GET /api/usuarios/{id}': 'Obtener usuario por ID (solo admin)',
                'PUT /api/usuarios/{id}': 'Actualizar usuario (solo admin)',
                'DELETE /api/usuarios/{id}': 'Eliminar usuario (solo admin)'
            },
            'dashboard': {
                'GET /api/dashboard/estadisticas': 'Obtener estadísticas del dashboard',
                'GET /api/dashboard/productos-mas-vendidos': 'Obtener productos más vendidos',
                'GET /api/dashboard/ventas-recientes': 'Obtener ventas recientes',
                'GET /api/dashboard/stock-bajo': 'Obtener productos con stock bajo'
            },
            'reportes': {
                'GET /api/reportes/ventas': 'Generar reporte de ventas',
                'GET /api/reportes/compras': 'Generar reporte de compras',
                'GET /api/reportes/inventario': 'Generar reporte de inventario',
                'GET /api/reportes/productos-mas-vendidos': 'Reporte de productos más vendidos'
            },
            'auditoria': {
                'GET /api/auditoria/logs': 'Obtener logs de auditoría (solo admin)',
                'GET /api/auditoria/logs/{id}': 'Obtener log específico (solo admin)',
                'GET /api/auditoria/logs/usuario/{id}': 'Obtener logs de usuario (solo admin)',
                'GET /api/auditoria/logs/tabla/{tabla}': 'Obtener logs de tabla (solo admin)',
                'GET /api/auditoria/logs/registro/{tabla}/{id}': 'Obtener historial de registro (solo admin)',
                'GET /api/auditoria/reporte': 'Generar reporte de auditoría (solo admin)',
                'GET /api/auditoria/estadisticas': 'Obtener estadísticas de auditoría (solo admin)'
            },
            'exportacion': {
                'GET /api/export/productos': 'Exportar productos',
                'GET /api/export/categorias': 'Exportar categorías',
                'GET /api/export/proveedores': 'Exportar proveedores',
                'GET /api/export/ventas': 'Exportar ventas',
                'GET /api/export/compras': 'Exportar compras',
                'GET /api/export/usuarios': 'Exportar usuarios (solo admin)',
                'GET /api/export/auditoria_logs': 'Exportar logs de auditoría (solo admin)'
            }
        },
        'autenticacion': {
            'tipo': 'Bearer Token (JWT)',
            'header': 'Authorization: Bearer <token>',
            'ejemplo': 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
        },
        'formatos_exportacion': {
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv'
        },
        'codigos_respuesta': {
            '200': 'OK - Operación exitosa',
            '201': 'Created - Recurso creado exitosamente',
            '400': 'Bad Request - Error en la solicitud',
            '401': 'Unauthorized - No autenticado',
            '403': 'Forbidden - Sin permisos',
            '404': 'Not Found - Recurso no encontrado',
            '500': 'Internal Server Error - Error del servidor'
        },
        'ejemplos': {
            'login': {
                'url': 'POST /api/auth/login',
                'body': {
                    'email': 'admin@ferreteria.com',
                    'password': 'admin123'
                },
                'response': {
                    'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'user': {
                        'id': 1,
                        'nombre': 'Administrador',
                        'email': 'admin@ferreteria.com',
                        'rol': 'admin'
                    }
                }
            },
            'crear_producto': {
                'url': 'POST /api/productos',
                'headers': {
                    'Authorization': 'Bearer <token>',
                    'Content-Type': 'application/json'
                },
                'body': {
                    'nombre': 'Martillo de Acero',
                    'descripcion': 'Martillo de acero con mango de madera',
                    'precio': 25.99,
                    'stock': 10,
                    'stock_minimo': 5,
                    'categoria_id': 1
                },
                'response': {
                    'id': 1,
                    'nombre': 'Martillo de Acero',
                    'descripcion': 'Martillo de acero con mango de madera',
                    'precio': 25.99,
                    'stock': 10,
                    'stock_minimo': 5,
                    'categoria_id': 1,
                    'created_at': '2024-01-01T00:00:00Z'
                }
            }
        }
    })

@docs_bp.route('/api/swagger')
def swagger_ui():
    """Interfaz de Swagger UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation - Sistema de Inventario Ferretería</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: '/api/docs',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "StandaloneLayout"
            });
        </script>
    </body>
    </html>
    """

def init_swagger(app):
    """Inicializar Swagger en la aplicación"""
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/api/docs.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/swagger"
    }
    
    swagger = Swagger(app, config=swagger_config)
    return swagger

from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from functools import wraps
from sqlalchemy import func, extract

from app import db
from app.models import (
    Categoria, Compra, DetalleVenta, Producto, Usuario, Venta, Proveedor
)
from app.extensions import cache, limiter

# Crear el Blueprint para las rutas de API
api = Blueprint('api', __name__)

# Ruta básica de bienvenida
@api.route('/')
def home():
    return jsonify({
        'message': 'API del Sistema de Inventario Ferretería',
        'version': '1.0',
        'status': 'funcionando',
        'endpoints': {
            'auth': '/api/auth/login',
            'productos': '/api/productos',
            'usuarios': '/api/usuarios',
            'categorias': '/api/categorias',
            'dashboard': '/api/dashboard/stats'
        }
    })

# Decorador para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token requerido'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Decorador para verificar rol
def rol_requerido(rol):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            print(f"🔍 ROL_REQUERIDO - Usuario: {current_user.nombre if current_user else 'None'}")
            print(f"🔍 ROL_REQUERIDO - Rol del usuario: {current_user.rol if current_user else 'None'}")
            print(f"🔍 ROL_REQUERIDO - Rol requerido: {rol}")
            if current_user.rol != rol:
                print(f"❌ ROL_REQUERIDO - ACCESO DENEGADO: {current_user.rol} != {rol}")
                return jsonify({'message': 'Permisos insuficientes'}), 403
            print("✅ ROL_REQUERIDO - ACCESO PERMITIDO")
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# Rutas de autenticación
@api.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json(silent=True) or {}
        # Aceptar tanto 'email' como 'username' para compatibilidad
        email = data.get('email') or data.get('username')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email y contraseña requeridos'}), 400
        
        user = Usuario.find_by_email(email)
        
        if user and user.check_password(password):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.now(timezone.utc) + timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            # Responder en formato consistente con create_response
            return jsonify({
                'data': {
                    'token': token,
                    'usuario': {
                        'id': user.id,
                        'nombre': user.nombre,
                        'email': user.email,
                        'rol': user.rol
                    }
                },
                'message': 'Login exitoso'
            }), 200
        
        return jsonify({'message': 'Credenciales inválidas'}), 401
        
    except Exception as e:
        return jsonify({'message': 'Error en el servidor', 'detail': str(e)}), 500

@api.route('/auth/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200

# Rutas de productos
@api.route('/productos', methods=['GET'])
@token_required
@cache.cached(timeout=300, query_string=True)
def get_productos(current_user):
    """Obtener todos los productos"""
    try:
        productos = Producto.query.all()
        return jsonify({
            'data': [{
                'id': p.id,
                'nombre': p.nombre,
                'descripcion': p.descripcion,
                'precio': float(p.precio),
                'stock': p.stock,
                'stock_minimo': p.stock_minimo,
                'categoria_id': p.categoria_id,
                'categoria': {
                    'id': p.categoria.id,
                    'nombre': p.categoria.nombre
                } if p.categoria else None
            } for p in productos]
        }), 200
        
    except Exception as e:
        print(f"Error al obtener productos: {str(e)}")
        return jsonify({'message': 'Error al obtener productos'}), 500

@api.route('/productos/<int:producto_id>', methods=['GET'])
@token_required
def get_producto(current_user, producto_id):
    """Obtener un producto específico"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        return jsonify({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': float(producto.precio),
            'stock': producto.stock,
            'stock_minimo': producto.stock_minimo,
            'categoria_id': producto.categoria_id,
            'categoria': {
                'id': producto.categoria.id,
                'nombre': producto.categoria.nombre
            } if producto.categoria else None
        }), 200
        
    except Exception as e:
        print(f"Error al obtener producto: {str(e)}")
        return jsonify({'message': 'Error al obtener producto'}), 500

@api.route('/productos', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_producto(current_user):
    """Crear nuevo producto (solo admin)"""
    try:
        data = request.get_json()
        
        nuevo_producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=data['precio'],
            stock=data['stock'],
            stock_minimo=data.get('stock_minimo', 5),
            categoria_id=data['categoria_id']
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'id': nuevo_producto.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear producto: {str(e)}")
        return jsonify({'message': 'Error al crear producto'}), 500

@api.route('/productos/<int:producto_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_producto(current_user, producto_id):
    """Actualizar producto (solo admin)"""
    try:
        print(f"\n{'='*80}")
        print(f"🔄 UPDATE PRODUCTO - ID: {producto_id}, Usuario: {current_user.nombre}")
        print(f"{'='*80}")
        
        producto = Producto.query.get_or_404(producto_id)
        print(f"✅ Producto encontrado: {producto.nombre}")
        
        data = request.get_json()
        print("📝 Datos recibidos del frontend:")
        for key, value in data.items():
            print(f"   - {key}: {value} (type: {type(value).__name__})")
        
        # Validar que la categoría existe si se proporciona
        if 'categoria_id' in data and data['categoria_id']:
            categoria = Categoria.query.get(data['categoria_id'])
            if not categoria:
                print(f"❌ Categoría ID {data['categoria_id']} no encontrada")
                return jsonify({'message': 'Categoría no encontrada'}), 404
            print(f"✅ Categoría validada: {categoria.nombre}")
        
        print("\n📊 Valores ANTES de actualizar:")
        print(f"   - nombre: {producto.nombre}")
        print(f"   - precio: {producto.precio}")
        print(f"   - stock: {producto.stock}")
        print(f"   - stock_minimo: {producto.stock_minimo}")
        print(f"   - categoria_id: {producto.categoria_id}")
        print(f"   - proveedor_id: {producto.proveedor_id}")
        
        # Actualizar campos
        if 'nombre' in data:
            producto.nombre = data['nombre']
            print(f"✏️  Actualizando nombre a: {data['nombre']}")
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
            print("✏️  Actualizando descripcion")
        if 'precio' in data:
            producto.precio = data['precio']
            print(f"✏️  Actualizando precio a: {data['precio']}")
        if 'stock' in data:
            producto.stock = data['stock']
            print(f"✏️  Actualizando stock a: {data['stock']}")
        if 'stock_minimo' in data:
            producto.stock_minimo = data['stock_minimo']
            print(f"✏️  Actualizando stock_minimo a: {data['stock_minimo']}")
        if 'categoria_id' in data:
            producto.categoria_id = data['categoria_id']
            print(f"✏️  Actualizando categoria_id a: {data['categoria_id']}")
        if 'proveedor_id' in data:
            producto.proveedor_id = data['proveedor_id']
            print(f"✏️  Actualizando proveedor_id a: {data['proveedor_id']}")
        if 'codigo_barras' in data:
            producto.codigo_barras = data['codigo_barras']
            print(f"✏️  Actualizando codigo_barras a: {data['codigo_barras']}")
        
        print("\n📊 Valores DESPUÉS de actualizar:")
        print(f"   - nombre: {producto.nombre}")
        print(f"   - precio: {producto.precio}")
        print(f"   - stock: {producto.stock}")
        print(f"   - stock_minimo: {producto.stock_minimo}")
        print(f"   - categoria_id: {producto.categoria_id}")
        print(f"   - proveedor_id: {producto.proveedor_id}")
        
        print("\n💾 Intentando hacer commit...")
        db.session.commit()
        print("✅ COMMIT EXITOSO!")
        print(f"{'='*80}\n")
        
        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'data': producto.to_dict()
        }), 200
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ ERROR en update_producto #{producto_id}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        print(f"📍 Mensaje: {str(e)}")
        print(f"📋 Detalles: {repr(e)}")
        print(f"{'='*80}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar producto: {str(e)}'}), 500

@api.route('/productos/<int:producto_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_producto(current_user, producto_id):
    """Eliminar producto (solo admin)"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        
        # Verificar si tiene ventas asociadas
        ventas_count = DetalleVenta.query.filter_by(producto_id=producto_id).count()
        if ventas_count > 0:
            return jsonify({
                'message': f'No se puede eliminar el producto porque tiene {ventas_count} ventas asociadas'
            }), 400
        
        # Verificar si tiene compras asociadas
        compras_count = Compra.query.filter_by(producto_id=producto_id).count()
        if compras_count > 0:
            return jsonify({
                'message': f'No se puede eliminar el producto porque tiene {compras_count} compras asociadas'
            }), 400
        
        db.session.delete(producto)
        db.session.commit()
        
        return jsonify({'message': 'Producto eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar producto: {str(e)}'}), 500

@api.route('/productos/search', methods=['GET'])
@token_required
def search_productos(current_user):
    """Buscar productos por nombre"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'message': 'Parámetro de búsqueda requerido'}), 400
            
        productos = Producto.query.filter(
            Producto.nombre.like(f'%{query}%')
        ).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'precio': float(p.precio),
            'stock': p.stock,
            'categoria': {
                'id': p.categoria.id,
                'nombre': p.categoria.nombre
            } if p.categoria else None
        } for p in productos]), 200
        
    except Exception as e:
        print(f"Error en la búsqueda: {str(e)}")
        return jsonify({'message': 'Error en la búsqueda'}), 500

@api.route('/productos/stock-bajo', methods=['GET'])
@token_required
def productos_stock_bajo(current_user):
    """Obtener productos con stock bajo"""
    try:
        productos = Producto.query.filter(
            Producto.stock <= Producto.stock_minimo
        ).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'stock': p.stock,
            'stock_minimo': p.stock_minimo,
            'categoria': {
                'id': p.categoria.id,
                'nombre': p.categoria.nombre
            } if p.categoria else None,
            'diferencia': p.stock_minimo - p.stock
        } for p in productos]), 200
        
    except Exception as e:
        print(f"Error al obtener productos con stock bajo: {str(e)}")
        return jsonify({'message': 'Error al obtener productos con stock bajo'}), 500

# Rutas de categorías
@api.route('/categorias', methods=['GET'])
@token_required
@cache.cached(timeout=300)
def get_categorias(current_user):
    """Obtener todas las categorías"""
    try:
        categorias = Categoria.query.all()
        return jsonify({
            'data': [{
                'id': c.id,
                'nombre': c.nombre,
                'descripcion': c.descripcion
            } for c in categorias]
        }), 200
        
    except Exception as e:
        print(f"Error al obtener categorías: {str(e)}")
        return jsonify({'message': 'Error al obtener categorías'}), 500

@api.route('/categorias', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_categoria(current_user):
    """Crear nueva categoría (solo admin)"""
    try:
        data = request.get_json()
        
        nueva_categoria = Categoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', '')
        )
        
        db.session.add(nueva_categoria)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría creada exitosamente',
            'id': nueva_categoria.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear categoría: {str(e)}")
        return jsonify({'message': 'Error al crear categoría'}), 500

@api.route('/categorias/<int:categoria_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_categoria(current_user, categoria_id):
    """Actualizar categoría (solo admin)"""
    try:
        print(f"🔄 UPDATE CATEGORIA - ID: {categoria_id}")
        categoria = Categoria.query.get_or_404(categoria_id)
        data = request.get_json()
        print(f"📝 Datos recibidos: {data}")
        
        categoria.nombre = data.get('nombre', categoria.nombre)
        categoria.descripcion = data.get('descripcion', categoria.descripcion)
        
        print("💾 Intentando hacer commit...")
        db.session.commit()
        print("✅ Commit exitoso!")
        
        return jsonify({'message': 'Categoría actualizada exitosamente', 'data': categoria.to_dict()}), 200
        
    except Exception as e:
        print(f"❌ ERROR en update_categoria: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar categoría: {str(e)}'}), 500

@api.route('/categorias/<int:categoria_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_categoria(current_user, categoria_id):
    """Eliminar categoría (solo admin)"""
    try:
        print(f"🗑️ DELETE CATEGORIA - ID: {categoria_id}")
        categoria = Categoria.query.get_or_404(categoria_id)
        print(f"📦 Categoría encontrada: {categoria.nombre}")
        
        # Verificar si la categoría tiene productos asociados
        productos_asociados = Producto.query.filter_by(categoria_id=categoria_id).count()
        print(f"🔍 Productos asociados: {productos_asociados}")
        if productos_asociados > 0:
            print(f"❌ No se puede eliminar - tiene {productos_asociados} productos")
            return jsonify({'message': f'No se puede eliminar la categoría porque tiene {productos_asociados} productos asociados'}), 400
        
        print("💾 Intentando eliminar...")
        db.session.delete(categoria)
        db.session.commit()
        print("✅ Categoría eliminada exitosamente!")
        
        return jsonify({'message': 'Categoría eliminada exitosamente'}), 200
        
    except Exception as e:
        print(f"❌ ERROR en delete_categoria: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar categoría: {str(e)}'}), 500

# Rutas de dashboard
@api.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Obtener estadísticas completas del dashboard"""
    try:
        # Mes actual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes anterior
        if datetime.now().month == 1:
            inicio_mes_anterior = datetime.now().replace(year=datetime.now().year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            inicio_mes_anterior = datetime.now().replace(month=datetime.now().month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        fin_mes_anterior = inicio_mes
        
        # Productos totales
        total_productos = Producto.query.count()
        
        # Productos con stock bajo
        productos_stock_bajo = Producto.query.filter(
            Producto.stock <= Producto.stock_minimo
        ).count()
        
        # Productos con stock crítico (0)
        productos_sin_stock = Producto.query.filter(Producto.stock == 0).count()
        
        # Ventas del mes actual
        ventas_mes = Venta.query.filter(Venta.fecha >= inicio_mes).count()
        ventas_mes_anterior = Venta.query.filter(
            Venta.fecha >= inicio_mes_anterior,
            Venta.fecha < fin_mes_anterior
        ).count()
        
        # Calcular cambio porcentual de ventas
        if ventas_mes_anterior > 0:
            cambio_ventas = ((ventas_mes - ventas_mes_anterior) / ventas_mes_anterior) * 100
        else:
            cambio_ventas = 100 if ventas_mes > 0 else 0
        
        # Ingresos del mes
        ingresos_mes = db.session.query(func.sum(Venta.total)).filter(
            Venta.fecha >= inicio_mes
        ).scalar() or 0
        
        ingresos_mes_anterior = db.session.query(func.sum(Venta.total)).filter(
            Venta.fecha >= inicio_mes_anterior,
            Venta.fecha < fin_mes_anterior
        ).scalar() or 0
        
        # Calcular cambio porcentual de ingresos
        if ingresos_mes_anterior > 0:
            cambio_ingresos = ((float(ingresos_mes) - float(ingresos_mes_anterior)) / float(ingresos_mes_anterior)) * 100
        else:
            cambio_ingresos = 100 if ingresos_mes > 0 else 0
        
        # Compras del mes
        compras_mes = Compra.query.filter(Compra.fecha_compra >= inicio_mes).count()
        
        gastos_mes = db.session.query(func.sum(Compra.total)).filter(
            Compra.fecha_compra >= inicio_mes
        ).scalar() or 0
        
        # Proveedores activos (con manejo de error si no existe el campo activo)
        try:
            proveedores_activos = Proveedor.query.filter(Proveedor.activo == True).count()
        except Exception:
            proveedores_activos = Proveedor.query.count()
        
        return jsonify({
            'total_productos': total_productos,
            'productos_stock_bajo': productos_stock_bajo,
            'productos_sin_stock': productos_sin_stock,
            'ventas_mes': ventas_mes,
            'ventas_mes_anterior': ventas_mes_anterior,
            'cambio_ventas': round(cambio_ventas, 2),
            'ingresos_mes': float(ingresos_mes),
            'ingresos_mes_anterior': float(ingresos_mes_anterior),
            'cambio_ingresos': round(cambio_ingresos, 2),
            'compras_mes': compras_mes,
            'gastos_mes': float(gastos_mes),
            'proveedores_activos': proveedores_activos,
            'margen_mes': float(ingresos_mes - gastos_mes)
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error en dashboard stats: {e}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error al obtener estadísticas: {str(e)}'}), 500

@api.route('/dashboard/ventas-recientes', methods=['GET'])
@token_required
def get_ventas_recientes(current_user):
    """Obtener ventas recientes"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        ventas = Venta.query.order_by(
            Venta.fecha.desc()
        ).limit(limit).all()
        
        return jsonify([{
            'id': v.id,
            'fecha': v.fecha.isoformat(),
            'total': float(v.total),
            'usuario': {
                'id': v.usuario.id,
                'nombre': v.usuario.nombre
            } if v.usuario else None
        } for v in ventas]), 200
        
    except Exception as e:
        import traceback
        print(f"Error en ventas recientes: {e}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error al obtener ventas recientes: {str(e)}'}), 500

@api.route('/dashboard/ventas-por-dia', methods=['GET'])
@token_required
def get_ventas_por_dia(current_user):
    """Obtener ventas de los últimos 7 días"""
    try:
        dias = int(request.args.get('dias', 7))
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        # Obtener ventas por día
        ventas_por_dia = db.session.query(
            func.date(Venta.fecha).label('fecha'),
            func.count(Venta.id).label('cantidad'),
            func.sum(Venta.total).label('total')
        ).filter(
            Venta.fecha >= fecha_inicio
        ).group_by(
            func.date(Venta.fecha)
        ).order_by(
            func.date(Venta.fecha)
        ).all()
        
        return jsonify([{
            'fecha': v.fecha.isoformat() if hasattr(v.fecha, 'isoformat') else str(v.fecha),
            'cantidad': v.cantidad,
            'total': float(v.total) if v.total else 0
        } for v in ventas_por_dia]), 200
        
    except Exception as e:
        import traceback
        print(f"Error en ventas por día: {e}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error al obtener ventas por día: {str(e)}'}), 500

@api.route('/dashboard/productos-mas-vendidos', methods=['GET'])
@token_required
def get_productos_mas_vendidos(current_user):
    """Obtener top productos más vendidos"""
    try:
        limit = int(request.args.get('limit', 5))
        dias = int(request.args.get('dias', 30))
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        # Obtener productos más vendidos
        productos = db.session.query(
            Producto.id,
            Producto.nombre,
            Producto.stock,
            func.sum(DetalleVenta.cantidad).label('total_vendido'),
            func.sum(DetalleVenta.subtotal).label('ingresos')
        ).join(
            DetalleVenta, Producto.id == DetalleVenta.producto_id
        ).join(
            Venta, DetalleVenta.venta_id == Venta.id
        ).filter(
            Venta.fecha >= fecha_inicio
        ).group_by(
            Producto.id, Producto.nombre, Producto.stock
        ).order_by(
            func.sum(DetalleVenta.cantidad).desc()
        ).limit(limit).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'stock': p.stock,
            'total_vendido': int(p.total_vendido),
            'ingresos': float(p.ingresos)
        } for p in productos]), 200
        
    except Exception as e:
        import traceback
        print(f"Error en productos más vendidos: {e}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error al obtener productos más vendidos: {str(e)}'}), 500

@api.route('/dashboard/stock-critico', methods=['GET'])
@token_required
def get_stock_critico(current_user):
    """Obtener productos con stock crítico"""
    try:
        productos = Producto.query.filter(
            Producto.stock <= Producto.stock_minimo
        ).order_by(
            Producto.stock.asc()
        ).limit(10).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'stock': p.stock,
            'stock_minimo': p.stock_minimo,
            'categoria': {
                'id': p.categoria.id,
                'nombre': p.categoria.nombre
            } if p.categoria else None
        } for p in productos]), 200
        
    except Exception as e:
        import traceback
        print(f"Error en stock crítico: {e}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error al obtener stock crítico: {str(e)}'}), 500

@api.route('/dashboard/actividad-reciente', methods=['GET'])
@token_required
def get_actividad_reciente(current_user):
    """Obtener actividad reciente (ventas y compras)"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # Obtener ventas recientes
        ventas = Venta.query.order_by(Venta.fecha.desc()).limit(limit // 2).all()
        
        # Obtener compras recientes
        compras = Compra.query.order_by(Compra.fecha_compra.desc()).limit(limit // 2).all()
        
        actividades = []
        
        for v in ventas:
            actividades.append({
                'tipo': 'venta',
                'id': v.id,
                'fecha': v.fecha.isoformat(),
                'total': float(v.total),
                'descripcion': f"Venta #{v.id}",
                'usuario': v.usuario.nombre if v.usuario else 'N/A'
            })
        
        for c in compras:
            actividades.append({
                'tipo': 'compra',
                'id': c.id,
                'fecha': c.fecha_compra.isoformat(),
                'total': float(c.total),
                'descripcion': f"Compra #{c.id}",
                'proveedor': c.proveedor.nombre if c.proveedor else 'N/A'
            })
        
        # Ordenar por fecha
        actividades.sort(key=lambda x: x['fecha'], reverse=True)
        
        return jsonify(actividades[:limit]), 200
        
    except Exception as e:
        import traceback
        print(f"Error en actividad reciente: {e}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error al obtener actividad reciente: {str(e)}'}), 500

# Rutas de usuarios
@api.route('/usuarios', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_usuarios(current_user):
    """Obtener todos los usuarios (solo admin)"""
    try:
        usuarios = Usuario.query.all()
        # Usar to_dict() para incluir todos los campos, incluido estado
        return jsonify([u.to_dict() for u in usuarios]), 200
        
    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        return jsonify({'message': 'Error al obtener usuarios'}), 500

@api.route('/usuarios', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_usuario(current_user):
    """Crear nuevo usuario (solo admin)"""
    try:
        data = request.get_json()
        
        # Verificar si el email ya existe
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'El email ya está registrado'}), 400
        
        # Convertir estado boolean a 1/0 para TINYINT(1)
        # Los administradores siempre están activos
        rol = data.get('rol', 'vendedor')
        if rol == 'admin':
            estado_activo = 1
        else:
            estado_activo = 1 if data.get('estado', True) else 0
        
        nuevo_usuario = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            rol=rol,
            activo=estado_activo
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'id': nuevo_usuario.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear usuario: {str(e)}")
        return jsonify({'message': 'Error al crear usuario'}), 500

@api.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_usuario(current_user, usuario_id):
    """Actualizar usuario (solo admin)"""
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        data = request.get_json() or {}

        # Validar email duplicado si cambia
        nuevo_email = data.get('email')
        if nuevo_email and nuevo_email != usuario.email:
            if Usuario.query.filter_by(email=nuevo_email).first():
                return jsonify({'message': 'El email ya está registrado'}), 400
            usuario.email = nuevo_email

        if 'nombre' in data and data['nombre']:
            usuario.nombre = data['nombre']

        if 'rol' in data and data['rol'] in ('admin', 'vendedor'):
            usuario.rol = data['rol']
        
        # Actualizar estado (mapear 'estado' del frontend a 'activo' en el modelo)
        # IMPORTANTE: El administrador siempre debe estar activo
        if 'estado' in data:
            rol_final = usuario.rol
            
            if rol_final == 'admin':
                usuario.activo = 1
            else:
                nuevo_estado = 1 if data['estado'] else 0
                usuario.activo = nuevo_estado

        if 'password' in data and data['password']:
            usuario.password = generate_password_hash(data['password'])
        
        db.session.commit()

        return jsonify({'message': 'Usuario actualizado exitosamente'}), 200
    except Exception as e:
        print(f"\n{'='*80}")
        print("[ERROR] ❌ Error al actualizar usuario")
        print(f"{'='*80}")
        print(f"[ERROR] Mensaje: {str(e)}")
        print(f"[ERROR] Tipo: {type(e).__name__}")
        print("[ERROR] Traceback completo:")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar usuario: {str(e)}'}), 500

@api.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_usuario(current_user, usuario_id):
    """Eliminar usuario (solo admin)"""
    try:
        # No permitir que el admin se elimine a sí mismo
        if current_user.id == usuario_id:
            return jsonify({'message': 'No puedes eliminar tu propio usuario'}), 400
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Verificar si tiene ventas asociadas
        ventas_count = Venta.query.filter_by(usuario_id=usuario_id).count()
        if ventas_count > 0:
            return jsonify({
                'message': f'No se puede eliminar el usuario porque tiene {ventas_count} ventas asociadas'
            }), 400
        
        # Verificar si tiene compras asociadas
        compras_count = Compra.query.filter_by(usuario_id=usuario_id).count()
        if compras_count > 0:
            return jsonify({
                'message': f'No se puede eliminar el usuario porque tiene {compras_count} compras asociadas'
            }), 400
        
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar usuario: {str(e)}'}), 500

# Rutas de ventas
@api.route('/ventas', methods=['GET'])
@token_required
def get_ventas(current_user):
    """Obtener ventas"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)  # Aumentado para mostrar más ventas
        
        ventas = Venta.query.order_by(
            Venta.fecha.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Si no hay paginación solicitada, devolver todas
        if page == 1 and per_page == 100:
            all_ventas = Venta.query.order_by(Venta.fecha.desc()).all()
            return jsonify({
                'data': [{
                    'id': v.id,
                    'fecha': v.fecha.isoformat() if v.fecha else None,
                    'total': float(v.total),
                    'cliente_nombre': v.cliente_nombre,
                    'cliente_documento': v.cliente_documento,
                    'cliente_telefono': v.cliente_telefono,
                    'usuario': {
                        'id': v.usuario.id,
                        'nombre': v.usuario.nombre
                    } if v.usuario else None,
                    'detalles': [{
                        'id': d.id,
                        'producto_id': d.producto_id,
                        'producto': {
                            'id': d.producto.id,
                            'nombre': d.producto.nombre
                        } if d.producto else None,
                        'cantidad': d.cantidad,
                        'precio_unitario': float(d.precio_unitario),
                        'subtotal': float(d.subtotal)
                    } for d in v.detalles]
                } for v in all_ventas]
            }), 200
        
        return jsonify({
            'data': {
                'ventas': [{
                    'id': v.id,
                    'fecha': v.fecha.isoformat() if v.fecha else None,
                    'total': float(v.total),
                    'cliente_nombre': v.cliente_nombre,
                    'cliente_documento': v.cliente_documento,
                    'cliente_telefono': v.cliente_telefono,
                    'usuario': {
                        'id': v.usuario.id,
                        'nombre': v.usuario.nombre
                    } if v.usuario else None,
                    'detalles': [{
                        'id': d.id,
                        'producto_id': d.producto_id,
                        'producto': {
                            'id': d.producto.id,
                            'nombre': d.producto.nombre
                        } if d.producto else None,
                        'cantidad': d.cantidad,
                        'precio_unitario': float(d.precio_unitario),
                        'subtotal': float(d.subtotal)
                    } for d in v.detalles]
                } for v in ventas.items],
                'total': ventas.total,
                'pages': ventas.pages,
                'current_page': ventas.page
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al obtener ventas', 'detail': str(e)}), 500

@api.route('/ventas', methods=['POST'])
@token_required
def create_venta(current_user):
    """Crear nueva venta"""
    try:
        data = request.get_json()
        
        if not data.get('detalles'):
            return jsonify({'message': 'La venta debe tener al menos un producto'}), 400
        
        # Validar que todos los detalles tengan cantidad > 0
        for detalle_data in data['detalles']:
            if detalle_data.get('cantidad', 0) <= 0:
                return jsonify({'message': 'La cantidad debe ser mayor a 0'}), 400
        
        # Validar stock ANTES de crear la venta (verificación robusta)
        productos_insuficientes = []
        for detalle_data in data['detalles']:
            producto = Producto.query.get(detalle_data['producto_id'])
            if not producto:
                return jsonify({'message': f'Producto {detalle_data["producto_id"]} no encontrado'}), 404
            
            if producto.stock < detalle_data['cantidad']:
                productos_insuficientes.append({
                    'nombre': producto.nombre,
                    'stock_disponible': producto.stock,
                    'cantidad_solicitada': detalle_data['cantidad']
                })
        
        # Si hay productos con stock insuficiente, devolver error detallado
        if productos_insuficientes:
            mensaje = 'Stock insuficiente para: ' + ', '.join([
                f"{p['nombre']} (disponible: {p['stock_disponible']}, solicitado: {p['cantidad_solicitada']})"
                for p in productos_insuficientes
            ])
            return jsonify({
                'message': mensaje,
                'productos_insuficientes': productos_insuficientes
            }), 400
        
        # Calcular total
        total = 0
        for detalle_data in data['detalles']:
            producto = Producto.query.get(detalle_data['producto_id'])
            cantidad = detalle_data['cantidad']
            precio_unitario = float(producto.precio)
            subtotal = cantidad * precio_unitario
            total += subtotal
        
        # Crear la venta
        nueva_venta = Venta(
            fecha=datetime.now(timezone.utc),
            total=total,
            usuario_id=current_user.id,
            cliente_nombre=data.get('cliente_nombre'),
            cliente_documento=data.get('cliente_documento'),
            cliente_telefono=data.get('cliente_telefono')
        )
        
        db.session.add(nueva_venta)
        db.session.flush()  # Para obtener el ID
        
        # Agregar detalles de venta
        for detalle_data in data['detalles']:
            producto = Producto.query.get(detalle_data['producto_id'])
            cantidad = detalle_data['cantidad']
            precio_unitario = float(producto.precio)
            subtotal = cantidad * precio_unitario
            
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=detalle_data['producto_id'],
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
            
            # Actualizar stock
            producto.stock -= cantidad
            
            db.session.add(detalle)
        
        db.session.commit()
        
        # Recargar venta con detalles para devolver respuesta completa
        venta_creada = Venta.query.get(nueva_venta.id)
        
        return jsonify({
            'data': {
                'id': venta_creada.id,
                'fecha': venta_creada.fecha.isoformat() if venta_creada.fecha else None,
                'total': float(venta_creada.total),
                'usuario': {
                    'id': venta_creada.usuario.id,
                    'nombre': venta_creada.usuario.nombre
                } if venta_creada.usuario else None,
                'detalles': [{
                    'id': d.id,
                    'producto_id': d.producto_id,
                    'cantidad': d.cantidad,
                    'precio_unitario': float(d.precio_unitario),
                    'subtotal': float(d.subtotal)
                } for d in venta_creada.detalles]
            },
            'message': 'Venta creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear venta', 'detail': str(e)}), 500

@api.route('/ventas/<int:venta_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def anular_venta(current_user, venta_id):
    """Anular/eliminar venta y restaurar stock (solo admin)"""
    try:
        print(f"🔍 DEBUG - Intentando anular venta {venta_id}")
        print(f"🔍 DEBUG - Usuario: {current_user.nombre}, Rol: {current_user.rol}")
        
        venta = Venta.query.get_or_404(venta_id)
        
        # Restaurar el stock de todos los productos
        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.producto_id)
            if producto:
                producto.stock += detalle.cantidad
                print(f"✅ Stock restaurado: {producto.nombre} +{detalle.cantidad} = {producto.stock}")
        
        # Registrar en auditoría la anulación
        from app.utils.auditoria import auditar_cambio_registro
        auditar_cambio_registro(
            usuario_id=current_user.id,
            accion='ANULAR',
            tabla_afectada='ventas',
            registro_id=venta.id,
            datos_anteriores={'total': float(venta.total), 'fecha': str(venta.fecha)}
        )
        
        # Eliminar detalles de venta
        for detalle in venta.detalles:
            db.session.delete(detalle)
        
        # Eliminar la venta
        db.session.delete(venta)
        db.session.commit()
        
        return jsonify({
            'message': 'Venta anulada exitosamente y stock restaurado'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error anulando venta: {str(e)}")
        return jsonify({'message': 'Error al anular venta', 'detail': str(e)}), 500

# Rutas de reportes
@api.route('/reportes/ventas-por-fecha', methods=['GET'])
@token_required
def reporte_ventas_por_fecha(current_user):
    """Reporte de ventas por rango de fechas"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'message': 'Fechas de inicio y fin requeridas'}), 400
        
        inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        ventas = Venta.query.filter(
            Venta.fecha >= inicio,
            Venta.fecha <= fin
        ).all()
        
        total_ventas = sum(float(v.total) for v in ventas)
        
        return jsonify({
            'ventas': [{
                'id': v.id,
                'fecha': v.fecha.isoformat(),
                'total': float(v.total),
                'usuario': v.usuario.nombre if v.usuario else None
            } for v in ventas],
            'total_ventas': total_ventas,
            'cantidad_ventas': len(ventas)
        }), 200
        
    except Exception as e:
        print(f"Error al generar reporte: {str(e)}")
        return jsonify({'message': 'Error al generar reporte'}), 500

@api.route('/reportes/productos-mas-vendidos', methods=['GET'])
@token_required
def reporte_productos_mas_vendidos(current_user):
    """Reporte de productos más vendidos"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        productos = db.session.query(
            Producto.id,
            Producto.nombre,
            func.sum(DetalleVenta.cantidad).label('total_vendido'),
            func.sum(DetalleVenta.subtotal).label('total_ingresos')
        ).join(
            DetalleVenta
        ).group_by(
            Producto.id, Producto.nombre
        ).order_by(
            func.sum(DetalleVenta.cantidad).desc()
        ).limit(limit).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'total_vendido': int(p.total_vendido),
            'total_ingresos': float(p.total_ingresos)
        } for p in productos]), 200
        
    except Exception as e:
        print(f"Error al generar reporte de productos más vendidos: {str(e)}")
        return jsonify({'message': 'Error al generar reporte'}), 500
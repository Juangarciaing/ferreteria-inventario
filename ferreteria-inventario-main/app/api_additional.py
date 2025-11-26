"""
Endpoints adicionales para la API
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import extract, func
from app import db
from app.models import (
    Categoria, Compra, DetalleVenta, Producto, Usuario, Venta, Proveedor
)

# Importar decoradores del archivo principal
from app.api_routes import token_required, rol_requerido

additional_api = Blueprint('additional_api', __name__, url_prefix='/api')

# --- Endpoints de Búsqueda de Productos ---
@additional_api.route('/productos/search', methods=['GET'])
@token_required
def search_productos(current_user):
    """Buscar productos por nombre"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'message': 'Parámetro de búsqueda requerido'}), 400
            
        productos = Producto.query.filter(
            Producto.nombre.like(f'%{query}%')
        ).join(Categoria).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'stock': p.stock,
            'stock_minimo': p.stock_minimo,
            'categoria': {
                'id': p.categoria.id,
                'nombre': p.categoria.nombre
            },
            'descripcion': p.descripcion,
            'created_at': p.created_at.isoformat()
        } for p in productos]), 200
        
    except Exception as e:
        print(f"Error al buscar productos: {str(e)}")
        return jsonify({'message': 'Error al buscar productos'}), 500

@additional_api.route('/productos/stock-bajo', methods=['GET'])
@token_required
def get_productos_stock_bajo(current_user):
    """Obtener productos con stock bajo"""
    try:
        productos = Producto.query.filter(
            Producto.stock <= Producto.stock_minimo
        ).join(Categoria).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'stock': p.stock,
            'stock_minimo': p.stock_minimo,
            'categoria': {
                'id': p.categoria.id,
                'nombre': p.categoria.nombre
            },
            'diferencia': p.stock_minimo - p.stock
        } for p in productos]), 200
        
    except Exception as e:
        print(f"Error al obtener productos con stock bajo: {str(e)}")
        return jsonify({'message': 'Error al obtener productos con stock bajo'}), 500

# --- Endpoints de Proveedores ---
@additional_api.route('/proveedores', methods=['GET'])
@token_required
def get_proveedores(current_user):
    """Obtener todos los proveedores"""
    try:
        proveedores = Proveedor.query.all()
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'contacto': p.contacto,
            'telefono': p.telefono,
            'email': p.email,
            'direccion': p.direccion,
            'rut_ruc': p.rut_ruc,
            'condiciones_pago': p.condiciones_pago,
            'descuento_default': float(p.descuento_default) if p.descuento_default else 0.0,
            'estado': p.estado,
            'rating': float(p.rating) if p.rating is not None else 0.0,
            'notas': p.notas,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in proveedores]), 200
        
    except Exception as e:
        print(f"Error al obtener proveedores: {str(e)}")
        return jsonify({'message': 'Error al obtener proveedores'}), 500

@additional_api.route('/proveedores', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_proveedor(current_user):
    """Crear nuevo proveedor (solo admin)"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['nombre', 'contacto']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Nombre y contacto son campos requeridos'}), 400
        
        # Verificar que no exista proveedor con mismo nombre
        if Proveedor.query.filter_by(nombre=data['nombre']).first():
            return jsonify({'message': 'Ya existe un proveedor con ese nombre'}), 400
        
        nuevo_proveedor = Proveedor(
            nombre=data['nombre'],
            contacto=data['contacto'],
            telefono=data.get('telefono'),
            email=data.get('email'),
            direccion=data.get('direccion'),
            rut_ruc=data.get('rut_ruc'),
            condiciones_pago=data.get('condiciones_pago', 'contado'),
            descuento_default=data.get('descuento_default', 0.0),
            estado=data.get('estado', 'activo'),
            rating=data.get('rating', 0),
            notas=data.get('notas')
        )
        
        db.session.add(nuevo_proveedor)
        db.session.commit()
        
        return jsonify({
            'id': nuevo_proveedor.id,
            'nombre': nuevo_proveedor.nombre,
            'contacto': nuevo_proveedor.contacto,
            'telefono': nuevo_proveedor.telefono,
            'email': nuevo_proveedor.email,
            'direccion': nuevo_proveedor.direccion,
            'rut_ruc': nuevo_proveedor.rut_ruc,
            'condiciones_pago': nuevo_proveedor.condiciones_pago,
            'descuento_default': float(nuevo_proveedor.descuento_default),
            'estado': nuevo_proveedor.estado,
            'rating': float(nuevo_proveedor.rating) if nuevo_proveedor.rating is not None else 0.0,
            'notas': nuevo_proveedor.notas,
            'created_at': nuevo_proveedor.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear proveedor: {str(e)}")
        return jsonify({'message': 'Error al crear proveedor'}), 500

@additional_api.route('/proveedores/<int:proveedor_id>', methods=['PUT'])
@token_required
@rol_requerido('admin')
def update_proveedor(current_user, proveedor_id):
    """Actualizar proveedor (solo admin)"""
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        data = request.get_json()
        
        # Verificar nombre duplicado si se está cambiando
        if data.get('nombre') and data['nombre'] != proveedor.nombre:
            existing = Proveedor.query.filter_by(nombre=data['nombre']).first()
            if existing:
                return jsonify({'message': 'Ya existe un proveedor con ese nombre'}), 400
        
        # Actualizar campos
        for field in ['nombre', 'contacto', 'telefono', 'email', 'direccion', 'rut_ruc', 'condiciones_pago', 'descuento_default', 'estado', 'rating', 'notas']:
            if field in data:
                setattr(proveedor, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Proveedor actualizado exitosamente',
            'data': {
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'contacto': proveedor.contacto,
                'telefono': proveedor.telefono,
                'email': proveedor.email,
                'direccion': proveedor.direccion,
                'rut_ruc': proveedor.rut_ruc,
                'condiciones_pago': proveedor.condiciones_pago,
                'descuento_default': float(proveedor.descuento_default) if proveedor.descuento_default else 0.0,
                'estado': proveedor.estado,
                'rating': float(proveedor.rating) if proveedor.rating is not None else 0.0,
                'notas': proveedor.notas,
                'created_at': proveedor.created_at.isoformat() if proveedor.created_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar proveedor: {str(e)}'}), 500

@additional_api.route('/proveedores/<int:proveedor_id>', methods=['DELETE'])
@token_required
@rol_requerido('admin')
def delete_proveedor(current_user, proveedor_id):
    """Eliminar proveedor (solo admin)"""
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        
        # Verificar si tiene productos asociados
        productos_count = Producto.query.filter_by(proveedor_id=proveedor_id).count()
        if productos_count > 0:
            return jsonify({
                'message': f'No se puede eliminar el proveedor porque tiene {productos_count} productos asociados'
            }), 400
        
        # Verificar si tiene compras asociadas
        compras_count = Compra.query.filter_by(proveedor_id=proveedor_id).count()
        if compras_count > 0:
            return jsonify({
                'message': f'No se puede eliminar el proveedor porque tiene {compras_count} compras asociadas'
            }), 400
        
        db.session.delete(proveedor)
        db.session.commit()
        
        return jsonify({'message': 'Proveedor eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar proveedor: {str(e)}'}), 500

# --- Endpoints de Compras ---
@additional_api.route('/compras', methods=['GET'])
@token_required
def get_compras(current_user):
    """Obtener todas las compras"""
    try:
        print(f"🔍 GET COMPRAS - Usuario: {current_user.nombre}")
        
        compras = Compra.query.options(
            db.joinedload(Compra.producto),
            db.joinedload(Compra.usuario),
            db.joinedload(Compra.proveedor)
        ).all()
        
        print(f"📦 Total compras encontradas: {len(compras)}")
        
        resultado = []
        for c in compras:
            try:
                compra_dict = {
                    'id': c.id,
                    'producto_id': c.producto_id,  # ✅ Agregar producto_id
                    'proveedor_id': c.proveedor_id,  # ✅ Agregar proveedor_id
                    'usuario_id': c.usuario_id,  # ✅ Agregar usuario_id
                    'producto': {
                        'id': c.producto.id,
                        'nombre': c.producto.nombre
                    } if c.producto else None,
                    'proveedor': {
                        'id': c.proveedor.id,
                        'nombre': c.proveedor.nombre
                    } if c.proveedor else None,
                    'usuario': {
                        'id': c.usuario.id,
                        'nombre': c.usuario.nombre
                    } if c.usuario else None,
                    'cantidad': c.cantidad,
                    'precio_unitario': float(c.precio_unitario),
                    'total': float(c.total),
                    'fecha_compra': c.fecha_compra.isoformat() if hasattr(c, 'fecha_compra') and c.fecha_compra else c.created_at.isoformat(),
                    'created_at': c.created_at.isoformat() if c.created_at else None
                }
                
                # Debug: imprimir primera compra para verificar estructura
                if c.id == compras[0].id:
                    print(f"📋 EJEMPLO de compra (ID {c.id}):")
                    print(f"   producto_id: {compra_dict['producto_id']} (type: {type(compra_dict['producto_id'])})")
                    print(f"   proveedor_id: {compra_dict['proveedor_id']} (type: {type(compra_dict['proveedor_id'])})")
                    print(f"   usuario_id: {compra_dict['usuario_id']} (type: {type(compra_dict['usuario_id'])})")
                
                resultado.append(compra_dict)
            except Exception as item_error:
                print(f"❌ Error procesando compra ID {c.id}: {str(item_error)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Compras procesadas exitosamente: {len(resultado)}")
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ ERROR en get_compras: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error al obtener compras: {str(e)}'}), 500

@additional_api.route('/compras', methods=['POST'])
@token_required
def create_compra(current_user):
    """Crear nueva compra y actualizar stock"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['producto_id', 'cantidad', 'precio_unitario']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Faltan campos requeridos'}), 400
        
        # Validar que el producto exista
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        # Calcular total
        total = float(data['cantidad']) * float(data['precio_unitario'])
        
        nueva_compra = Compra(
            producto_id=data['producto_id'],
            cantidad=data['cantidad'],
            precio_unitario=data['precio_unitario'],
            total=total,
            proveedor_id=data.get('proveedor_id'),
            usuario_id=current_user.id
        )
        
        db.session.add(nueva_compra)
        
        # Actualizar stock del producto
        producto.stock += int(data['cantidad'])
        
        db.session.commit()
        
        return jsonify({
            'id': nueva_compra.id,
            'producto_id': nueva_compra.producto_id,
            'cantidad': nueva_compra.cantidad,
            'precio_unitario': float(nueva_compra.precio_unitario),
            'total': float(nueva_compra.total),
            'proveedor_id': nueva_compra.proveedor_id,
            'usuario_id': nueva_compra.usuario_id,
            'created_at': nueva_compra.created_at.isoformat(),
            'stock_actualizado': producto.stock
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear compra: {str(e)}")
        return jsonify({'message': 'Error al crear compra'}), 500

@additional_api.route('/compras/<int:compra_id>', methods=['PUT'])
@token_required
def update_compra(current_user, compra_id):
    """Actualizar una compra"""
    try:
        print(f"🔄 UPDATE COMPRA #{compra_id} - Usuario: {current_user.nombre}")
        
        compra = Compra.query.get(compra_id)
        if not compra:
            return jsonify({'message': 'Compra no encontrada'}), 404
        
        data = request.get_json()
        
        # Si cambia la cantidad o el producto, ajustamos el stock
        producto_anterior = compra.producto
        cantidad_anterior = compra.cantidad
        
        # Actualizar campos
        if 'producto_id' in data:
            # Si cambia de producto, restamos del anterior y sumamos al nuevo
            if data['producto_id'] != compra.producto_id:
                producto_nuevo = Producto.query.get(data['producto_id'])
                if not producto_nuevo:
                    return jsonify({'message': 'Producto nuevo no encontrado'}), 404
                
                # Restar del producto anterior
                producto_anterior.stock -= cantidad_anterior
                # Sumar al nuevo
                producto_nuevo.stock += cantidad_anterior
                
                compra.producto_id = data['producto_id']
        
        if 'cantidad' in data:
            # Ajustar stock por diferencia de cantidad
            diferencia = int(data['cantidad']) - cantidad_anterior
            compra.producto.stock += diferencia
            compra.cantidad = data['cantidad']
        
        if 'precio_unitario' in data:
            compra.precio_unitario = data['precio_unitario']
        
        if 'proveedor_id' in data:
            compra.proveedor_id = data['proveedor_id']
        
        # Recalcular total
        compra.total = compra.cantidad * compra.precio_unitario
        
        db.session.commit()
        print(f"✅ Compra #{compra_id} actualizada exitosamente")
        
        return jsonify({
            'message': 'Compra actualizada exitosamente',
            'data': {
                'id': compra.id,
                'producto_id': compra.producto_id,
                'cantidad': compra.cantidad,
                'precio_unitario': float(compra.precio_unitario),
                'total': float(compra.total),
                'proveedor_id': compra.proveedor_id,
                'usuario_id': compra.usuario_id,
                'fecha_compra': compra.fecha_compra.isoformat() if compra.fecha_compra else None,
                'created_at': compra.created_at.isoformat() if compra.created_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando compra #{compra_id}: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        print(f"📍 Detalles: {repr(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error al actualizar compra: {str(e)}'}), 500

@additional_api.route('/compras/<int:compra_id>', methods=['DELETE'])
@token_required
def delete_compra(current_user, compra_id):
    """Eliminar una compra y ajustar stock"""
    try:
        print(f"🗑️ DELETE COMPRA #{compra_id} - Usuario: {current_user.nombre}")
        
        compra = Compra.query.get(compra_id)
        if not compra:
            return jsonify({'message': 'Compra no encontrada'}), 404
        
        # Ajustar el stock del producto (restar la cantidad comprada)
        producto = compra.producto
        if producto:
            producto.stock -= compra.cantidad
            print(f"📦 Stock de '{producto.nombre}' ajustado: {producto.stock + compra.cantidad} -> {producto.stock}")
        
        db.session.delete(compra)
        db.session.commit()
        
        print(f"✅ Compra #{compra_id} eliminada exitosamente")
        return jsonify({'message': 'Compra eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error eliminando compra #{compra_id}: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        print(f"📍 Detalles: {repr(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error al eliminar compra: {str(e)}'}), 500

# --- Endpoints de Reportes ---
@additional_api.route('/reportes/ventas-por-fecha', methods=['GET'])
@token_required
def get_ventas_por_fecha(current_user):
    """Obtener reporte de ventas por fecha"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'message': 'Fechas de inicio y fin son requeridas'}), 400
        
        fecha_inicio = datetime.fromisoformat(fecha_inicio)
        fecha_fin = datetime.fromisoformat(fecha_fin)
        
        ventas = db.session.query(
            func.date(Venta.fecha).label('fecha'),
            func.sum(Venta.total).label('total'),
            func.count(Venta.id).label('cantidad_ventas')
        ).filter(
            Venta.fecha >= fecha_inicio,
            Venta.fecha <= fecha_fin
        ).group_by(func.date(Venta.fecha)).all()
        
        return jsonify([{
            'fecha': v.fecha.isoformat(),
            'total': float(v.total),
            'cantidad_ventas': v.cantidad_ventas
        } for v in ventas]), 200
        
    except Exception as e:
        print(f"Error al generar reporte: {str(e)}")
        return jsonify({'message': 'Error al generar reporte'}), 500

@additional_api.route('/reportes/productos-mas-vendidos', methods=['GET'])
@token_required
def get_productos_mas_vendidos(current_user):
    """Obtener productos más vendidos"""
    try:
        limite = request.args.get('limite', 10, type=int)
        
        productos = db.session.query(
            Producto.id,
            Producto.nombre,
            func.sum(DetalleVenta.cantidad).label('total_vendido'),
            func.sum(DetalleVenta.subtotal).label('ingresos_totales')
        ).join(
            DetalleVenta, Producto.id == DetalleVenta.producto_id
        ).group_by(
            Producto.id, Producto.nombre
        ).order_by(
            func.sum(DetalleVenta.cantidad).desc()
        ).limit(limite).all()
        
        return jsonify([{
            'producto_id': p.id,
            'nombre': p.nombre,
            'total_vendido': int(p.total_vendido),
            'ingresos_totales': float(p.ingresos_totales)
        } for p in productos]), 200
        
    except Exception as e:
        print(f"Error al obtener productos más vendidos: {str(e)}")
        return jsonify({'message': 'Error al obtener productos más vendidos'}), 500
"""
Utilidades para exportación de datos
"""
import io
import csv
from datetime import datetime
from flask import make_response
from app import db
from app.models import Producto, Venta, Compra, Usuario, Categoria, Proveedor

def export_productos_csv():
    """Exportar productos a CSV"""
    productos = Producto.query.join(Categoria).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Stock Mínimo',
        'Categoría', 'Proveedor', 'Fecha Creación'
    ])
    
    # Data
    for producto in productos:
        writer.writerow([
            producto.id,
            producto.nombre,
            producto.descripcion or '',
            float(producto.precio),
            producto.stock,
            producto.stock_minimo,
            producto.categoria.nombre if producto.categoria else '',
            producto.proveedor.nombre if producto.proveedor else '',
            producto.created_at.strftime('%Y-%m-%d %H:%M:%S') if producto.created_at else ''
        ])
    
    output.seek(0)
    return output.getvalue()

def export_ventas_csv(fecha_inicio=None, fecha_fin=None):
    """Exportar ventas a CSV"""
    query = Venta.query.join(Usuario)
    
    if fecha_inicio:
        query = query.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Venta.fecha <= fecha_fin)
    
    ventas = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Fecha', 'Total', 'Usuario', 'Cliente', 'Productos'
    ])
    
    # Data
    for venta in ventas:
        productos_str = ', '.join([
            f"{detalle.producto.nombre} (x{detalle.cantidad})" 
            for detalle in venta.detalles
        ]) if venta.detalles else ''
        
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%Y-%m-%d %H:%M:%S') if venta.fecha else '',
            float(venta.total),
            venta.usuario.nombre if venta.usuario else '',
            getattr(venta, 'cliente_nombre', '') or '',
            productos_str
        ])
    
    output.seek(0)
    return output.getvalue()

def export_compras_csv(fecha_inicio=None, fecha_fin=None):
    """Exportar compras a CSV"""
    query = Compra.query.join(Producto).join(Usuario)
    
    if fecha_inicio:
        query = query.filter(Compra.created_at >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Compra.created_at <= fecha_fin)
    
    compras = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Fecha', 'Producto', 'Cantidad', 'Precio Unitario', 
        'Total', 'Usuario', 'Proveedor'
    ])
    
    # Data
    for compra in compras:
        writer.writerow([
            compra.id,
            compra.created_at.strftime('%Y-%m-%d %H:%M:%S') if compra.created_at else '',
            compra.producto.nombre if compra.producto else '',
            compra.cantidad,
            float(compra.precio_unitario),
            float(compra.total),
            compra.usuario.nombre if compra.usuario else '',
            compra.proveedor.nombre if compra.proveedor else ''
        ])
    
    output.seek(0)
    return output.getvalue()

def export_usuarios_csv():
    """Exportar usuarios a CSV"""
    usuarios = Usuario.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Nombre', 'Email', 'Rol', 'Teléfono', 'Dirección', 'Fecha Creación'
    ])
    
    # Data
    for usuario in usuarios:
        writer.writerow([
            usuario.id,
            usuario.nombre,
            usuario.email,
            usuario.rol,
            usuario.telefono or '',
            usuario.direccion or '',
            usuario.created_at.strftime('%Y-%m-%d %H:%M:%S') if usuario.created_at else ''
        ])
    
    output.seek(0)
    return output.getvalue()

def export_proveedores_csv():
    """Exportar proveedores a CSV"""
    proveedores = Proveedor.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Nombre', 'Contacto', 'Teléfono', 'Email', 'Dirección',
        'Condiciones Pago', 'Descuento Default', 'Estado', 'Rating', 'Fecha Creación'
    ])
    
    # Data
    for proveedor in proveedores:
        writer.writerow([
            proveedor.id,
            proveedor.nombre,
            proveedor.contacto,
            proveedor.telefono or '',
            proveedor.email or '',
            proveedor.direccion or '',
            proveedor.condiciones_pago or '',
            float(proveedor.descuento_default) if proveedor.descuento_default else 0,
            proveedor.estado,
            float(proveedor.rating) if proveedor.rating else 0,
            proveedor.created_at.strftime('%Y-%m-%d %H:%M:%S') if proveedor.created_at else ''
        ])
    
    output.seek(0)
    return output.getvalue()

def create_csv_response(csv_data, filename):
    """Crear respuesta HTTP para CSV"""
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return response

def export_inventario_completo():
    """Exportar inventario completo con estadísticas"""
    productos = Producto.query.join(Categoria).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Stock Mínimo',
        'Categoría', 'Proveedor', 'Estado Stock', 'Valor Inventario', 'Fecha Creación'
    ])
    
    # Data
    for producto in productos:
        estado_stock = 'Bajo' if producto.stock <= producto.stock_minimo else 'Normal'
        valor_inventario = float(producto.precio) * producto.stock
        
        writer.writerow([
            producto.id,
            producto.nombre,
            producto.descripcion or '',
            float(producto.precio),
            producto.stock,
            producto.stock_minimo,
            producto.categoria.nombre if producto.categoria else '',
            producto.proveedor.nombre if producto.proveedor else '',
            estado_stock,
            valor_inventario,
            producto.created_at.strftime('%Y-%m-%d %H:%M:%S') if producto.created_at else ''
        ])
    
    output.seek(0)
    return output.getvalue()

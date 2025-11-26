"""
Endpoints para exportación de datos
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.api_routes import token_required, rol_requerido
from app.utils.export import (
    export_productos_csv, export_ventas_csv, export_compras_csv,
    export_usuarios_csv, export_proveedores_csv, export_inventario_completo,
    create_csv_response
)

export_api = Blueprint('export_api', __name__, url_prefix='/api')

@export_api.route('/export/productos', methods=['GET'])
@token_required
def export_productos(current_user):
    """Exportar productos a CSV"""
    try:
        csv_data = export_productos_csv()
        return create_csv_response(csv_data, 'productos')
    except Exception as e:
        return jsonify({'message': 'Error al exportar productos'}), 500

@export_api.route('/export/ventas', methods=['GET'])
@token_required
def export_ventas(current_user):
    """Exportar ventas a CSV"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = datetime.fromisoformat(fecha_inicio)
        if fecha_fin:
            fecha_fin_obj = datetime.fromisoformat(fecha_fin)
        
        csv_data = export_ventas_csv(fecha_inicio_obj, fecha_fin_obj)
        return create_csv_response(csv_data, 'ventas')
    except Exception as e:
        return jsonify({'message': 'Error al exportar ventas'}), 500

@export_api.route('/export/compras', methods=['GET'])
@token_required
def export_compras(current_user):
    """Exportar compras a CSV"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = datetime.fromisoformat(fecha_inicio)
        if fecha_fin:
            fecha_fin_obj = datetime.fromisoformat(fecha_fin)
        
        csv_data = export_compras_csv(fecha_inicio_obj, fecha_fin_obj)
        return create_csv_response(csv_data, 'compras')
    except Exception as e:
        return jsonify({'message': 'Error al exportar compras'}), 500

@export_api.route('/export/usuarios', methods=['GET'])
@token_required
@rol_requerido('admin')
def export_usuarios(current_user):
    """Exportar usuarios a CSV (solo admin)"""
    try:
        csv_data = export_usuarios_csv()
        return create_csv_response(csv_data, 'usuarios')
    except Exception as e:
        return jsonify({'message': 'Error al exportar usuarios'}), 500

@export_api.route('/export/proveedores', methods=['GET'])
@token_required
def export_proveedores(current_user):
    """Exportar proveedores a CSV"""
    try:
        csv_data = export_proveedores_csv()
        return create_csv_response(csv_data, 'proveedores')
    except Exception as e:
        return jsonify({'message': 'Error al exportar proveedores'}), 500

@export_api.route('/export/inventario', methods=['GET'])
@token_required
def export_inventario(current_user):
    """Exportar inventario completo a CSV"""
    try:
        csv_data = export_inventario_completo()
        return create_csv_response(csv_data, 'inventario_completo')
    except Exception as e:
        return jsonify({'message': 'Error al exportar inventario'}), 500

@export_api.route('/export/reporte-ventas', methods=['GET'])
@token_required
def export_reporte_ventas(current_user):
    """Exportar reporte detallado de ventas"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'message': 'Fechas de inicio y fin requeridas'}), 400
        
        fecha_inicio_obj = datetime.fromisoformat(fecha_inicio)
        fecha_fin_obj = datetime.fromisoformat(fecha_fin)
        
        csv_data = export_ventas_csv(fecha_inicio_obj, fecha_fin_obj)
        return create_csv_response(csv_data, 'reporte_ventas')
    except Exception as e:
        return jsonify({'message': 'Error al exportar reporte de ventas'}), 500

@export_api.route('/export/stock-bajo', methods=['GET'])
@token_required
def export_stock_bajo(current_user):
    """Exportar productos con stock bajo"""
    try:
        from app.models import Producto, Categoria
        
        productos_stock_bajo = Producto.query.filter(
            Producto.stock <= Producto.stock_minimo
        ).join(Categoria).all()
        
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'ID', 'Nombre', 'Categoría', 'Stock Actual', 'Stock Mínimo',
            'Diferencia', 'Precio', 'Valor Inventario', 'Proveedor'
        ])
        
        # Data
        for producto in productos_stock_bajo:
            diferencia = producto.stock_minimo - producto.stock
            valor_inventario = float(producto.precio) * producto.stock
            
            writer.writerow([
                producto.id,
                producto.nombre,
                producto.categoria.nombre if producto.categoria else '',
                producto.stock,
                producto.stock_minimo,
                diferencia,
                float(producto.precio),
                valor_inventario,
                producto.proveedor.nombre if producto.proveedor else ''
            ])
        
        output.seek(0)
        csv_data = output.getvalue()
        
        return create_csv_response(csv_data, 'stock_bajo')
    except Exception as e:
        return jsonify({'message': 'Error al exportar stock bajo'}), 500

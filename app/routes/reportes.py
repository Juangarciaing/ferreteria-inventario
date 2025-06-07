from datetime import datetime, timedelta
from io import BytesIO
from flask import make_response, render_template, request
from flask_login import login_required
from sqlalchemy import extract, func
from xhtml2pdf import pisa

from app import db
from app.models import Categoria, DetalleVenta, Producto, Usuario, Venta
from . import main, rol_requerido

@main.route('/reportes/ventas')
@login_required
@rol_requerido('admin')
def reporte_ventas():
    """Reporte de ventas por mes (solo admin)."""
    ventas_por_mes = db.session.query(
        extract('month', Venta.fecha).label('mes'),
        func.sum(Venta.total).label('total')
    ).group_by('mes').order_by('mes').all()

    meses = [f"Mes {int(v[0])}" for v in ventas_por_mes]
    totales = [float(v[1]) for v in ventas_por_mes]

    return render_template('reporte_ventas.html', meses=meses, totales=totales)

@main.route('/reportes/ventas_fecha', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def ventas_por_fecha():
    """Reporte de ventas por rango de fechas (solo admin)."""
    ventas = []
    total = 0
    fecha_inicio = ''
    fecha_fin = ''

    if request.method == 'POST':
        fecha_inicio = request.form['inicio']
        fecha_fin = request.form['fin']

        inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

        ventas = Venta.query.filter(Venta.fecha.between(inicio_dt, fin_dt)).order_by(Venta.fecha).all()
        total = sum(float(v.total) for v in ventas)

    return render_template('ventas_fecha.html', ventas=ventas, total=total,
                           fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

@main.route('/reportes/ventas_fecha/pdf', methods=['POST'])
@login_required
@rol_requerido('admin')
def exportar_ventas_pdf():
    """Exporta a PDF el reporte de ventas por fecha (solo admin)."""
    fecha_inicio = request.form['inicio']
    fecha_fin = request.form['fin']

    inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

    ventas = Venta.query.filter(Venta.fecha.between(inicio_dt, fin_dt)).order_by(Venta.fecha).all()
    total = sum(float(v.total) for v in ventas)

    html = render_template('ventas_pdf.html', ventas=ventas, total=total, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_ventas.pdf'
    return response

@main.route('/reportes/ventas_por_usuario')
@login_required
@rol_requerido('admin')
def ventas_por_usuario():
    """Reporte de ventas agrupadas por usuario (solo admin)."""
    resultados = db.session.query(
        Usuario.nombre,
        db.func.count(Venta.id).label('cantidad_ventas'),
        db.func.sum(Venta.total).label('total_ventas')
    ).join(Venta, Venta.usuario_id == Usuario.id) \
     .group_by(Usuario.id) \
     .all()

    total_ventas = sum(r.cantidad_ventas or 0 for r in resultados)
    total_monto = sum(r.total_ventas or 0 for r in resultados)

    return render_template(
        'ventas_por_usuario.html',
        resultados=resultados,
        total_ventas=total_ventas,
        total_monto=total_monto
    )

@main.route('/reportes/ventas_por_usuario/pdf')
@login_required
@rol_requerido('admin')
def ventas_por_usuario_pdf():
    """Exporta a PDF el reporte de ventas por usuario (solo admin)."""
    resultados = db.session.query(
        Usuario.nombre,
        db.func.count(Venta.id).label('cantidad_ventas'),
        db.func.sum(Venta.total).label('total_ventas')
    ).join(Venta, Venta.usuario_id == Usuario.id) \
     .group_by(Usuario.id) \
     .all()

    fecha_actual = datetime.now()

    html = render_template('ventas_por_usuario_pdf.html', resultados=resultados, fecha_actual=fecha_actual)
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="ventas_por_usuario.pdf"'
    return response

@main.route('/reporte/general')
@login_required
def reporte_general():
    """Genera un reporte general con estadísticas del sistema."""
    hoy = datetime.now()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    seis_meses_atras = hoy - timedelta(days=180)

    # 1. Top 5 productos más vendidos del mes actual
    top_productos = (
        db.session.query(Producto.nombre, func.sum(DetalleVenta.cantidad).label('total'))
        .join(DetalleVenta)
        .join(Venta)
        .filter(Venta.fecha >= inicio_mes)
        .group_by(Producto.id)
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .limit(5)
        .all()
    )

    nombres_top = [r[0] for r in top_productos]
    cantidades_top = [int(r[1]) for r in top_productos]

    # 2. Total de ventas por mes (últimos 6 meses)
    ventas_mensuales = (
        db.session.query(func.date_format(Venta.fecha, "%Y-%m").label("mes"), func.sum(Venta.total))
        .filter(Venta.fecha >= seis_meses_atras)
        .group_by("mes")
        .order_by("mes")
        .all()
    )
    meses = [r[0] for r in ventas_mensuales]
    totales = [float(r[1]) for r in ventas_mensuales]

    # 3. Ventas por categoría del mes actual
    ventas_categoria = (
        db.session.query(
            Categoria.nombre.label('categoria'),
            func.coalesce(func.sum(DetalleVenta.subtotal), 0).label('total_categoria')
        )
        .join(Producto, Categoria.id == Producto.categoria_id)
        .join(DetalleVenta, Producto.id == DetalleVenta.producto_id)
        .join(Venta, DetalleVenta.venta_id == Venta.id)
        .filter(Venta.fecha >= inicio_mes)
        .group_by(Categoria.id)
        .all()
    )
    categorias = [r.categoria for r in ventas_categoria]
    totales_categoria = [float(r.total_categoria) for r in ventas_categoria]

    return render_template(
        'reporte_general.html',
        nombres_top=nombres_top,
        cantidades_top=cantidades_top,
        meses=meses,
        totales=totales,
        categorias=categorias,
        totales_categoria=totales_categoria
    )

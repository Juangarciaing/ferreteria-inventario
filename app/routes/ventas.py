from decimal import Decimal
from io import BytesIO
from flask import flash, make_response, redirect, render_template, request, url_for, current_app
from flask_login import login_required, current_user
from xhtml2pdf import pisa

from app import db
from app.models import DetalleVenta, Producto, Usuario, Venta
from . import main, rol_requerido

@main.route('/ventas/registrar', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'vendedor')
def registrar_venta():
    """Permite registrar una venta (admin o vendedor)."""
    productos = Producto.query.all()

    if request.method == 'POST':
        try:
            seleccionados = request.form.getlist('productos')
            detalles = []
            total = Decimal('0.00')

            if not seleccionados:
                flash("Debes seleccionar al menos un producto.")
                return redirect(url_for('main.registrar_venta'))

            for id_str in seleccionados:
                id_producto = int(id_str)
                cantidad_raw = request.form.get(f'cantidad_{id_producto}', '').strip()

                if not cantidad_raw or not cantidad_raw.isdigit():
                    flash("Cantidad inválida.")
                    return redirect(url_for('main.registrar_venta'))

                cantidad = int(cantidad_raw)
                if cantidad <= 0:
                    flash("Cantidad debe ser mayor a cero.")
                    return redirect(url_for('main.registrar_venta'))

                producto = Producto.query.get(id_producto)
                if not producto:
                    flash("Producto no encontrado.")
                    return redirect(url_for('main.registrar_venta'))

                if producto.stock < cantidad:
                    flash(f"No hay suficiente stock para {producto.nombre}")
                    return redirect(url_for('main.registrar_venta'))

                subtotal = producto.precio * cantidad
                total += subtotal
                producto.stock -= cantidad

                detalle = DetalleVenta(
                    producto_id=id_producto,
                    cantidad=cantidad,
                    subtotal=subtotal
                )
                detalles.append(detalle)

            venta = Venta(usuario_id=current_user.id, total=total)
            db.session.add(venta)
            db.session.flush()

            for d in detalles:
                d.venta_id = venta.id
                db.session.add(d)

            db.session.commit()
            flash("✅ Venta registrada correctamente.")
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al registrar venta: {e}")
            flash("❌ Error interno al procesar la venta.")
            return redirect(url_for('main.registrar_venta'))

    return render_template('registrar_venta.html', productos=productos)

@main.route('/ventas')
@login_required
@rol_requerido('admin')
def ventas():
    """Lista todas las ventas (solo admin)."""
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('ventas.html', ventas=ventas)

@main.route('/ventas/<int:id>')
@login_required
def detalle_venta(id):
    """Muestra el detalle de una venta específica."""
    venta = Venta.query.get_or_404(id)

    # Si el usuario es vendedor y no es el dueño de la venta, se bloquea el acceso
    if current_user.rol == 'vendedor' and venta.usuario_id != current_user.id:
        flash("No tienes permiso para ver esta venta.")
        return redirect(url_for('main.dashboard'))

    detalles = DetalleVenta.query.filter_by(venta_id=id).all()
    vendedor = Usuario.query.get(venta.usuario_id)

    return render_template('detalle_venta.html', venta=venta, detalles=detalles, vendedor=vendedor)

@main.route('/ventas/<int:id>/pdf')
@login_required
def factura_pdf(id):
    """Genera la factura en PDF de una venta."""
    venta = Venta.query.get_or_404(id)
    detalles = DetalleVenta.query.filter_by(venta_id=id).all()
    vendedor = Usuario.query.get(venta.usuario_id)
    html = render_template('factura_pdf.html', venta=venta, detalles=detalles, vendedor=vendedor)

    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    return make_response(pdf.read(), {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=factura_venta_{venta.id}.pdf'
    })

@main.route('/mis_ventas')
@login_required
@rol_requerido('vendedor')
def mis_ventas():
    """Muestra las ventas realizadas por el usuario vendedor."""
    ventas = Venta.query.filter_by(usuario_id=current_user.id).order_by(Venta.fecha.desc()).all()
    return render_template('mis_ventas.html', ventas=ventas)

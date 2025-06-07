from decimal import Decimal
from flask import flash, redirect, render_template, request, url_for, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Compra, Producto
from . import main, rol_requerido

@main.route('/compras/registrar', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def registrar_compra():
    """Permite registrar una compra y actualizar el stock (solo admin)."""
    productos = Producto.query.all()

    if request.method == 'POST':
        try:
            producto_id = int(request.form['producto_id'])
            cantidad = int(request.form['cantidad'])
            precio_unitario = Decimal(request.form['precio_unitario'])
            total = precio_unitario * cantidad

            compra = Compra(
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total=total,
                usuario_id=current_user.id
            )
            db.session.add(compra)

            # Actualizar stock del producto comprado
            producto = Producto.query.get(producto_id)
            producto.stock += cantidad

            db.session.commit()
            flash('Compra registrada y stock actualizado')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al registrar compra: {e}")
            flash('Error al registrar la compra.')
            return redirect(url_for('main.registrar_compra'))

    return render_template('registrar_compra.html', productos=productos)

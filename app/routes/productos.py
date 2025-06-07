from flask import flash, redirect, render_template, request, url_for, current_app
from flask_login import login_required

from app import db
from app.models import Categoria, Producto
from . import main, rol_requerido

@main.route('/productos')
@login_required
@rol_requerido('admin')
def productos():
    """Lista todos los productos (solo admin)."""
    lista = Producto.query.all()
    return render_template('productos.html', productos=lista)

@main.route('/productos/agregar', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def agregar_producto():
    """Permite al admin agregar un producto."""
    categorias = Categoria.query.all()

    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria_id = request.form['categoria_id']
        try:
            precio = float(request.form['precio'])
            stock = int(request.form['stock'])
            stock_minimo = int(request.form['stock_minimo'])
        except ValueError:
            flash('Datos inválidos.')
            return redirect(url_for('main.agregar_producto'))

        nuevo = Producto(
            nombre=nombre,
            categoria_id=categoria_id,
            precio=precio,
            stock=stock,
            stock_minimo=stock_minimo
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto agregado correctamente')
        return redirect(url_for('main.productos'))

    return render_template('agregar_producto.html', categorias=categorias)

@main.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def editar_producto(id):
    """Permite al admin editar un producto existente."""
    producto = Producto.query.get_or_404(id)
    categorias = Categoria.query.all()

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.categoria_id = request.form['categoria_id']
        try:
            producto.precio = float(request.form['precio'])
            producto.stock = int(request.form['stock'])
            producto.stock_minimo = int(request.form['stock_minimo'])
        except ValueError:
            flash('Datos inválidos.')
            return redirect(url_for('main.editar_producto', id=id))

        db.session.commit()
        flash('Producto actualizado')
        return redirect(url_for('main.productos'))

    return render_template('editar_producto.html', producto=producto, categorias=categorias)

@main.route('/productos/eliminar/<int:id>')
@login_required
@rol_requerido('admin')
def eliminar_producto(id):
    """Permite al admin eliminar un producto."""
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado')
    return redirect(url_for('main.productos'))

@main.route('/productos/buscar', methods=['GET'])
@login_required
@rol_requerido('admin', 'vendedor')
def buscar_productos():
    """Permite buscar productos por nombre y categoría (admin y vendedor)."""
    nombre = request.args.get('nombre', '').strip()
    categoria_id = request.args.get('categoria', '')

    query = Producto.query

    if nombre:
        query = query.filter(Producto.nombre.ilike(f'%{nombre}%'))

    if categoria_id and categoria_id.isdigit():
        query = query.filter_by(categoria_id=int(categoria_id))

    productos = query.all()
    categorias = Categoria.query.all()

    return render_template('buscar_productos.html', productos=productos, categorias=categorias, nombre=nombre, categoria_id=categoria_id)

@main.route('/stock/alertas')
@login_required
@rol_requerido('admin', 'vendedor')
def alertas_stock():
    """Muestra productos con stock bajo (admin y vendedor)."""
    margen = current_app.config.get('MARGEN_STOCK', 2)
    productos = Producto.query.filter(
        (Producto.stock <= (Producto.stock_minimo + margen))
    ).all()
    return render_template('alertas_stock.html', productos=productos)

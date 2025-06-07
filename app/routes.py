from datetime import datetime, timedelta
from io import BytesIO

from flask import (
    Blueprint, flash, make_response, redirect, render_template,
    request, url_for, current_app
)
from flask_login import (
    current_user, login_required, login_user, logout_user
)
from sqlalchemy import extract, func
from werkzeug.security import check_password_hash, generate_password_hash
from xhtml2pdf import pisa

from app import db
from app.models import (
    Categoria, Compra, DetalleVenta, Producto, Usuario, Venta
)

from functools import wraps

main = Blueprint('main', __name__)

# --- Decorador para roles ---
def rol_requerido(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.rol not in roles:
                flash('Acceso no autorizado')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Rutas ---

@main.route('/')
def home():
    """Redirige a la página de login."""
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios."""
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['contraseña']
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and check_password_hash(usuario.contraseña, clave):
            if usuario.estado != 'activo':
                flash('Tu cuenta está inactiva. Contacta al administrador.')
                return redirect(url_for('main.login'))

            login_user(usuario)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciales inválidas')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario."""
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    """Muestra el panel principal del usuario autenticado."""
    return render_template('dashboard.html', usuario=current_user)

@main.route('/admin/registrar_usuario', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def registrar_usuario():
    """Permite al admin registrar un nuevo usuario."""
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        clave = request.form['contraseña']
        rol = request.form['rol']

        # Validaciones de unicidad
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado.')
        elif Usuario.query.filter_by(cedula=cedula).first():
            flash('La cédula ya está registrada.')
        else:
            nueva_clave = generate_password_hash(clave)
            nuevo_usuario = Usuario(
                nombre=nombre,
                cedula=cedula,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                contraseña=nueva_clave,
                rol=rol
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario registrado correctamente.')
            return redirect(url_for('main.dashboard'))

    return render_template('registrar_usuario.html')

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
            total = 0

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

                subtotal = float(producto.precio) * cantidad
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
            precio_unitario = float(request.form['precio_unitario'])
            total = cantidad * precio_unitario

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

@main.route('/usuarios')
@login_required
@rol_requerido('admin')
def listar_usuarios():
    """Lista todos los usuarios (solo admin)."""
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios, usuario=current_user)

@main.route('/usuarios/toggle/<int:id>', methods=['POST'])
@login_required
@rol_requerido('admin')
def cambiar_estado_usuario(id):
    """Activa o desactiva un usuario (solo admin)."""
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash('No puedes cambiar el estado de tu propio usuario.')
        return redirect(url_for('main.listar_usuarios'))

    usuario.estado = 'inactivo' if usuario.estado == 'activo' else 'activo'
    db.session.commit()
    flash(f"Usuario {'desactivado' if usuario.estado == 'inactivo' else 'activado'} correctamente.")
    return redirect(url_for('main.listar_usuarios'))

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

    # Calcular totales generales en Python
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

@main.route('/ventas/<int:id>/pdf')
@login_required
def factura_pdf(id):
    """Genera la factura en PDF de una venta."""
    venta = Venta.query.get_or_404(id)

    # Si el usuario es vendedor y no es el dueño de la venta, se bloquea el acceso
    if current_user.rol == 'vendedor' and venta.usuario_id != current_user.id:
        flash("No tienes permiso para ver esta venta.")
        return redirect(url_for('main.dashboard'))

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

@main.route('/mis_ventas')
@login_required
@rol_requerido('vendedor')
def mis_ventas():
    """Muestra las ventas realizadas por el usuario vendedor."""
    ventas = Venta.query.filter_by(usuario_id=current_user.id).order_by(Venta.fecha.desc()).all()
    return render_template('mis_ventas.html', ventas=ventas)

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

@main.route('/mi_perfil')
@login_required
def mi_perfil():
    """Muestra el perfil del usuario actual."""
    return render_template('perfil.html', usuario=current_user)

@main.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Permite al usuario editar su perfil."""
    if request.method == 'POST':
        current_user.nombre = request.form['nombre']
        current_user.telefono = request.form['telefono']
        current_user.direccion = request.form['direccion']
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('main.mi_perfil'))

    return render_template('editar_perfil.html', usuario=current_user)

@main.route('/perfil/contraseña', methods=['GET', 'POST'])
@login_required
def cambiar_contraseña():
    """Permite al usuario cambiar su contraseña."""
    if request.method == 'POST':
        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        if not check_password_hash(current_user.contraseña, actual):
            flash('Contraseña actual incorrecta.')
        elif nueva != confirmar:
            flash('La nueva contraseña no coincide.')
        else:
            current_user.contraseña = generate_password_hash(nueva)
            db.session.commit()
            flash('Contraseña actualizada exitosamente.')
            return redirect(url_for('main.mi_perfil'))

    return render_template('cambiar_contraseña.html')

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
    # Extrae nombres de categorías y totales, asegurando que no haya None
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
"""
Script para poblar la base de datos con datos de prueba
Crea productos, categorías, proveedores, ventas y compras de ejemplo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Producto, Categoria, Proveedor, Usuario, Venta, DetalleVenta, Compra
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def poblar_datos():
    app = create_app()
    with app.app_context():
        print("🗑️  Limpiando datos anteriores...")
        # Limpiar en orden correcto (respetando foreign keys)
        DetalleVenta.query.delete()
        Venta.query.delete()
        Compra.query.delete()
        Producto.query.delete()
        Categoria.query.delete()
        Proveedor.query.delete()
        # NO borrar usuarios para mantener admin
        db.session.commit()
        
        print("📦 Creando categorías...")
        categorias_data = [
            {"nombre": "Herramientas Manuales", "descripcion": "Martillos, destornilladores, llaves"},
            {"nombre": "Herramientas Eléctricas", "descripcion": "Taladros, sierras, amoladoras"},
            {"nombre": "Tornillería y Fijación", "descripcion": "Tornillos, clavos, tarugos"},
            {"nombre": "Electricidad", "descripcion": "Cables, enchufes, interruptores"},
            {"nombre": "Fontanería", "descripcion": "Tuberías, llaves, accesorios"},
            {"nombre": "Pintura y Acabados", "descripcion": "Pinturas, brochas, rodillos"},
            {"nombre": "Adhesivos y Selladores", "descripcion": "Pegamentos, siliconas, cintas"},
            {"nombre": "Ferretería General", "descripcion": "Bisagras, cerraduras, candados"},
            {"nombre": "Seguridad Industrial", "descripcion": "Cascos, guantes, gafas"},
            {"nombre": "Material de Construcción", "descripcion": "Cemento, arena, ladrillos"},
            {"nombre": "Jardinería", "descripcion": "Palas, rastrillos, mangueras"},
            {"nombre": "Iluminación", "descripcion": "Focos, lámparas, reflectores"}
        ]
        
        categorias = []
        for cat_data in categorias_data:
            cat = Categoria(**cat_data)
            db.session.add(cat)
            db.session.flush()  # Flush para obtener el ID
            categorias.append(cat)
        db.session.commit()
        print(f"   ✅ {len(categorias)} categorías creadas")
        
        print("🏢 Creando proveedores...")
        proveedores_data = [
            {
                "nombre": "Distribuidora Ferretek S.A.",
                "contacto": "Juan Pérez",
                "telefono": "+51 987654321",
                "email": "ventas@ferretek.com",
                "direccion": "Av. Industrial 123, Lima",
                "rut_ruc": "20123456789",
                "condiciones_pago": "30 días",
                "descuento_default": 5.0,
                "estado": "activo",
                "rating": 4.5,
                "notas": "Proveedor principal de herramientas"
            },
            {
                "nombre": "Importadora El Tornillo E.I.R.L.",
                "contacto": "María González",
                "telefono": "+51 912345678",
                "email": "compras@eltornillo.pe",
                "direccion": "Jr. Los Pinos 456, Callao",
                "rut_ruc": "20234567890",
                "condiciones_pago": "15 días",
                "descuento_default": 3.5,
                "estado": "activo",
                "rating": 4.0,
                "notas": "Especialistas en tornillería"
            },
            {
                "nombre": "Suministros Industriales SAC",
                "contacto": "Carlos Rodríguez",
                "telefono": "+51 998765432",
                "email": "ventas@suministros.com",
                "direccion": "Av. Grau 789, Arequipa",
                "rut_ruc": "20345678901",
                "condiciones_pago": "45 días",
                "descuento_default": 7.0,
                "estado": "activo",
                "rating": 5.0,
                "notas": "Mejores precios en volumen"
            },
            {
                "nombre": "Ferretería Global S.R.L.",
                "contacto": "Ana López",
                "telefono": "+51 923456789",
                "email": "info@ferreteriaglobal.pe",
                "direccion": "Calle Real 321, Cusco",
                "rut_ruc": "20456789012",
                "condiciones_pago": "20 días",
                "descuento_default": 4.0,
                "estado": "activo",
                "rating": 4.2
            },
            {
                "nombre": "Materiales del Norte",
                "contacto": "Roberto Sánchez",
                "telefono": "+51 945678901",
                "email": "ventas@materialesnorte.com",
                "direccion": "Av. Panamá 555, Trujillo",
                "rut_ruc": "20567890123",
                "condiciones_pago": "60 días",
                "descuento_default": 6.5,
                "estado": "activo",
                "rating": 3.8
            }
        ]
        
        proveedores = []
        for prov_data in proveedores_data:
            prov = Proveedor(**prov_data)
            db.session.add(prov)
            db.session.flush()  # Flush para obtener el ID
            proveedores.append(prov)
        db.session.commit()
        print(f"   ✅ {len(proveedores)} proveedores creados")
        
        print("📦 Creando productos...")
        productos_data = [
            # Herramientas Manuales
            {"nombre": "Martillo de Acero 16 oz", "precio": 12.50, "stock": 45, "stock_minimo": 10, "categoria_id": 1, "proveedor_id": 1, "descripcion": "Martillo profesional con mango ergonómico"},
            {"nombre": "Destornillador Phillips #2", "precio": 3.75, "stock": 120, "stock_minimo": 30, "categoria_id": 1, "proveedor_id": 1, "descripcion": "Destornillador magnético de alta resistencia"},
            {"nombre": "Alicate Universal 8\"", "precio": 8.90, "stock": 35, "stock_minimo": 15, "categoria_id": 1, "proveedor_id": 2, "descripcion": "Alicate con empuñadura antideslizante"},
            {"nombre": "Llave Inglesa 12\"", "precio": 15.00, "stock": 28, "stock_minimo": 8, "categoria_id": 1, "proveedor_id": 2, "descripcion": "Llave ajustable cromada"},
            {"nombre": "Sierra de Mano 18\"", "precio": 10.50, "stock": 22, "stock_minimo": 8, "categoria_id": 1, "proveedor_id": 1, "descripcion": "Sierra con hoja de acero templado"},
            
            # Herramientas Eléctricas
            {"nombre": "Taladro Percutor 1/2\" 600W", "precio": 85.00, "stock": 15, "stock_minimo": 5, "categoria_id": 2, "proveedor_id": 3, "descripcion": "Taladro profesional con maletín"},
            {"nombre": "Amoladora Angular 4.5\" 850W", "precio": 72.50, "stock": 12, "stock_minimo": 4, "categoria_id": 2, "proveedor_id": 3, "descripcion": "Amoladora con disco de corte incluido"},
            {"nombre": "Sierra Circular 7.25\" 1200W", "precio": 95.00, "stock": 8, "stock_minimo": 3, "categoria_id": 2, "proveedor_id": 3, "descripcion": "Sierra con guía láser"},
            {"nombre": "Lijadora Orbital 200W", "precio": 48.00, "stock": 10, "stock_minimo": 4, "categoria_id": 2, "proveedor_id": 4, "descripcion": "Lijadora con bolsa recolectora de polvo"},
            
            # Tornillería
            {"nombre": "Tornillos Autorroscantes 1\" x100", "precio": 4.20, "stock": 250, "stock_minimo": 50, "categoria_id": 3, "proveedor_id": 2, "descripcion": "Caja con 100 unidades"},
            {"nombre": "Clavos de Acero 2\" x1kg", "precio": 3.50, "stock": 180, "stock_minimo": 40, "categoria_id": 3, "proveedor_id": 2, "descripcion": "Clavos de construcción"},
            {"nombre": "Pernos y Tuercas M8 x50", "precio": 8.90, "stock": 95, "stock_minimo": 30, "categoria_id": 3, "proveedor_id": 2, "descripcion": "Pack de 50 juegos"},
            {"nombre": "Tarugos Plásticos 6mm x100", "precio": 2.80, "stock": 320, "stock_minimo": 80, "categoria_id": 3, "proveedor_id": 2, "descripcion": "Para todo tipo de paredes"},
            
            # Electricidad
            {"nombre": "Cable THHN 12 AWG x100m", "precio": 125.00, "stock": 45, "stock_minimo": 10, "categoria_id": 4, "proveedor_id": 4, "descripcion": "Cable eléctrico certificado"},
            {"nombre": "Interruptor Simple Blanco", "precio": 2.50, "stock": 150, "stock_minimo": 40, "categoria_id": 4, "proveedor_id": 4, "descripcion": "Interruptor 10A 250V"},
            {"nombre": "Tomacorriente Doble c/Tierra", "precio": 4.80, "stock": 88, "stock_minimo": 25, "categoria_id": 4, "proveedor_id": 4, "descripcion": "Tomacorriente polarizado"},
            {"nombre": "Cinta Aislante Negra 3M", "precio": 1.90, "stock": 200, "stock_minimo": 50, "categoria_id": 4, "proveedor_id": 1, "descripcion": "Cinta adhesiva 18mm x 20m"},
            {"nombre": "Foco LED 9W Luz Blanca", "precio": 6.50, "stock": 145, "stock_minimo": 30, "categoria_id": 4, "proveedor_id": 5, "descripcion": "Equivalente a 60W"},
            
            # Fontanería
            {"nombre": "Tubo PVC 1/2\" x3m", "precio": 5.80, "stock": 68, "stock_minimo": 20, "categoria_id": 5, "proveedor_id": 5, "descripcion": "Tubo presión clase 10"},
            {"nombre": "Codo PVC 1/2\" 90°", "precio": 0.85, "stock": 240, "stock_minimo": 60, "categoria_id": 5, "proveedor_id": 5, "descripcion": "Accesorio de presión"},
            {"nombre": "Llave de Paso 1/2\"", "precio": 12.50, "stock": 32, "stock_minimo": 10, "categoria_id": 5, "proveedor_id": 5, "descripcion": "Llave esférica de bronce"},
            {"nombre": "Cinta Teflón 12mm", "precio": 0.90, "stock": 185, "stock_minimo": 50, "categoria_id": 5, "proveedor_id": 1, "descripcion": "Rollo de 12m"},
            
            # Pintura
            {"nombre": "Pintura Látex Blanca 1 Gal", "precio": 18.50, "stock": 55, "stock_minimo": 15, "categoria_id": 6, "proveedor_id": 3, "descripcion": "Pintura lavable interior"},
            {"nombre": "Brocha 2\" Profesional", "precio": 5.20, "stock": 75, "stock_minimo": 20, "categoria_id": 6, "proveedor_id": 3, "descripcion": "Brocha de cerda mixta"},
            {"nombre": "Rodillo 9\" con Bandeja", "precio": 8.90, "stock": 42, "stock_minimo": 12, "categoria_id": 6, "proveedor_id": 3, "descripcion": "Kit para pintar paredes"},
            {"nombre": "Thinner Acrílico 1L", "precio": 6.80, "stock": 38, "stock_minimo": 10, "categoria_id": 6, "proveedor_id": 4, "descripcion": "Diluyente para pinturas"},
            
            # Adhesivos
            {"nombre": "Silicona Transparente 280ml", "precio": 4.50, "stock": 92, "stock_minimo": 25, "categoria_id": 7, "proveedor_id": 1, "descripcion": "Sellador multiuso"},
            {"nombre": "Pegamento Contacto 1L", "precio": 12.00, "stock": 48, "stock_minimo": 15, "categoria_id": 7, "proveedor_id": 4, "descripcion": "Adhesivo de contacto fuerte"},
            {"nombre": "Cinta Masking 1\" x40m", "precio": 2.30, "stock": 165, "stock_minimo": 40, "categoria_id": 7, "proveedor_id": 1, "descripcion": "Cinta de papel"},
            
            # Ferretería General
            {"nombre": "Bisagra para Puerta 4\"", "precio": 3.80, "stock": 125, "stock_minimo": 30, "categoria_id": 8, "proveedor_id": 2, "descripcion": "Bisagra de acero"},
            {"nombre": "Cerradura de Sobreponer", "precio": 15.50, "stock": 28, "stock_minimo": 8, "categoria_id": 8, "proveedor_id": 2, "descripcion": "Con 3 llaves"},
            {"nombre": "Candado de Acero 40mm", "precio": 8.90, "stock": 54, "stock_minimo": 15, "categoria_id": 8, "proveedor_id": 2, "descripcion": "Candado con arco protegido"},
            
            # Seguridad
            {"nombre": "Casco de Seguridad", "precio": 12.50, "stock": 35, "stock_minimo": 10, "categoria_id": 9, "proveedor_id": 5, "descripcion": "Casco ajustable certificado"},
            {"nombre": "Guantes de Seguridad Par", "precio": 4.20, "stock": 88, "stock_minimo": 25, "categoria_id": 9, "proveedor_id": 5, "descripcion": "Guantes de cuero"},
            {"nombre": "Gafas Protectoras", "precio": 6.80, "stock": 62, "stock_minimo": 20, "categoria_id": 9, "proveedor_id": 5, "descripcion": "Lentes antiempañantes"},
            
            # Construcción
            {"nombre": "Cemento Tipo I 42.5kg", "precio": 22.50, "stock": 85, "stock_minimo": 20, "categoria_id": 10, "proveedor_id": 3, "descripcion": "Cemento Portland"},
            {"nombre": "Arena Gruesa x Saco", "precio": 8.00, "stock": 120, "stock_minimo": 30, "categoria_id": 10, "proveedor_id": 3, "descripcion": "Saco de 40kg"},
            
            # Jardinería
            {"nombre": "Pala de Jardín", "precio": 14.50, "stock": 32, "stock_minimo": 10, "categoria_id": 11, "proveedor_id": 1, "descripcion": "Pala con mango de madera"},
            {"nombre": "Manguera 1/2\" x15m", "precio": 18.90, "stock": 25, "stock_minimo": 8, "categoria_id": 11, "proveedor_id": 5, "descripcion": "Manguera reforzada"},
            
            # Iluminación
            {"nombre": "Reflector LED 50W", "precio": 35.00, "stock": 18, "stock_minimo": 5, "categoria_id": 12, "proveedor_id": 5, "descripcion": "Reflector para exteriores"},
            {"nombre": "Lámpara Fluorescente 18W", "precio": 8.50, "stock": 45, "stock_minimo": 15, "categoria_id": 12, "proveedor_id": 4, "descripcion": "Tubo LED integrado"}
        ]
        
        productos = []
        for i, prod_data in enumerate(productos_data, 1):
            prod_data['codigo_barras'] = f"77{str(i).zfill(10)}"
            prod = Producto(**prod_data)
            db.session.add(prod)
            productos.append(prod)
        db.session.commit()
        print(f"   ✅ {len(productos)} productos creados")
        
        print("💰 Creando compras históricas...")
        # Obtener usuario admin
        admin = Usuario.query.filter_by(email="admin@ferreteria.com").first()
        if not admin:
            print("   ⚠️  Usuario admin no encontrado")
            return
        
        # Crear compras de los últimos 3 meses
        compras_creadas = 0
        for dias_atras in range(90, 0, -7):  # Cada 7 días
            fecha_compra = datetime.now() - timedelta(days=dias_atras)
            # 2-4 compras por semana
            for _ in range(random.randint(2, 4)):
                proveedor = random.choice(proveedores)
                producto = random.choice(productos)
                cantidad = random.randint(10, 50)
                precio_unitario = producto.precio * random.uniform(0.6, 0.8)  # Precio de compra menor
                
                compra = Compra(
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=round(precio_unitario, 2),
                    total=round(precio_unitario * cantidad, 2),
                    proveedor_id=proveedor.id,
                    usuario_id=admin.id,
                    fecha_compra=fecha_compra
                )
                db.session.add(compra)
                compras_creadas += 1
        
        db.session.commit()
        print(f"   ✅ {compras_creadas} compras creadas")
        
        print("🛒 Creando ventas históricas...")
        # Crear ventas de los últimos 2 meses
        ventas_creadas = 0
        for dias_atras in range(60, 0, -1):  # Cada día
            fecha_venta = datetime.now() - timedelta(days=dias_atras)
            # 1-5 ventas por día
            for _ in range(random.randint(1, 5)):
                # Crear venta con 1-4 productos
                num_productos = random.randint(1, 4)
                productos_venta = random.sample(productos, num_productos)
                
                venta = Venta(
                    usuario_id=admin.id,
                    fecha=fecha_venta,
                    cliente_nombre=random.choice([
                        "Juan Pérez", "María García", "Carlos López", 
                        "Ana Martínez", "Roberto Sánchez", "Laura Torres",
                        None  # Algunas ventas sin cliente
                    ])
                )
                db.session.add(venta)
                db.session.flush()  # Para obtener el ID
                
                total = 0
                for producto in productos_venta:
                    cantidad = random.randint(1, 5)
                    subtotal = producto.precio * cantidad
                    total += subtotal
                    
                    detalle = DetalleVenta(
                        venta_id=venta.id,
                        producto_id=producto.id,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                        subtotal=subtotal
                    )
                    db.session.add(detalle)
                
                venta.total = round(total, 2)
                ventas_creadas += 1
        
        db.session.commit()
        print(f"   ✅ {ventas_creadas} ventas creadas")
        
        print("\n" + "="*60)
        print("✅ Base de datos poblada exitosamente!")
        print("="*60)
        print("\n📊 Resumen:")
        print(f"   • Categorías: {len(categorias)}")
        print(f"   • Proveedores: {len(proveedores)}")
        print(f"   • Productos: {len(productos)}")
        print(f"   • Compras: {compras_creadas}")
        print(f"   • Ventas: {ventas_creadas}")
        print("\n🔐 Credenciales:")
        print("   Email: admin@ferreteria.com")
        print("   Password: admin123")
        print()

if __name__ == "__main__":
    poblar_datos()

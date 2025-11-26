"""
Script para ejecutar la aplicación Flask con arquitectura limpia
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from app import create_app, db

def create_tables():
    """Crear tablas de la base de datos"""
    try:
        db.create_all()
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")

def seed_data():
    """Insertar datos iniciales"""
    try:
        from app.models import Usuario, Categoria, Proveedor, Producto
        
        # Verificar si ya hay datos
        if Usuario.query.count() > 0:
            print("✅ Datos iniciales ya existen")
            return True
            
        print("🌱 Insertando datos iniciales...")
        
        # Crear usuarios - Contraseñas desde variables de entorno
        admin_password = os.environ.get('ADMIN_DEFAULT_PASSWORD')
        vendedor_password = os.environ.get('VENDEDOR_DEFAULT_PASSWORD')
        
        if not admin_password or not vendedor_password:
            raise ValueError("Las contraseñas por defecto no están configuradas. Define ADMIN_DEFAULT_PASSWORD y VENDEDOR_DEFAULT_PASSWORD")
        
        usuarios_data = [
            {
                'nombre': 'Administrador',
                'email': 'admin@ferreteria.com',
                'password': admin_password,
                'rol': 'admin',
                'telefono': '555-0001',
                'direccion': 'Oficina Principal'
            },
            {
                'nombre': 'Juan Pérez',
                'email': 'vendedor@ferreteria.com',
                'password': vendedor_password,
                'rol': 'vendedor',
                'telefono': '555-0002',
                'direccion': 'Sucursal Norte'
            },
            {
                'nombre': 'María González',
                'email': 'maria@ferreteria.com',
                'password': vendedor_password,
                'rol': 'vendedor',
                'telefono': '555-0003',
                'direccion': 'Sucursal Sur'
            }
        ]
        
        usuarios = []
        for data in usuarios_data:
            usuario = Usuario(
                nombre=data['nombre'],
                email=data['email'],
                rol=data['rol'],
                telefono=data['telefono'],
                direccion=data['direccion']
            )
            usuario.set_password(data['password'])
            usuario.save()
            usuarios.append(usuario)
        
        # Crear categorías
        categorias_data = [
            'Herramientas Manuales',
            'Herramientas Eléctricas', 
            'Tornillería y Fijación',
            'Electricidad',
            'Fontanería',
            'Pintura y Acabados',
            'Adhesivos y Selladores',
            'Ferretería General',
            'Seguridad Industrial',
            'Material de Construcción',
            'Jardinería',
            'Iluminación'
        ]
        
        categorias = []
        for nombre in categorias_data:
            categoria = Categoria(nombre=nombre)
            categoria.save()
            categorias.append(categoria)
        
        # Crear proveedores
        proveedores_data = [
            {
                'nombre': 'Distribuidora Central',
                'contacto': 'Carlos Ramírez',
                'telefono': '555-1001',
                'email': 'ventas@distcentral.com',
                'direccion': 'Av. Principal 123, Industrial',
                'condiciones_pago': 'credito_30',
                'descuento_default': 5.0,
                'estado': 'activo',
                'rating': 4.5
            },
            {
                'nombre': 'Herramientas del Norte',
                'contacto': 'Ana López',
                'telefono': '555-1002',
                'email': 'pedidos@herranorte.com',
                'direccion': 'Zona Industrial Norte',
                'condiciones_pago': 'credito_15',
                'descuento_default': 3.0,
                'estado': 'activo',
                'rating': 4.8
            },
            {
                'nombre': 'Suministros Técnicos',
                'contacto': 'Miguel Torres',
                'telefono': '555-1003',
                'email': 'info@sumtecnicos.com',
                'direccion': 'Calle Comercio 456',
                'condiciones_pago': 'credito_45',
                'descuento_default': 2.0,
                'estado': 'activo',
                'rating': 4.2
            }
        ]
        
        proveedores = []
        for data in proveedores_data:
            proveedor = Proveedor(**data)
            proveedor.save()
            proveedores.append(proveedor)
        
        # Crear productos de ejemplo
        productos_data = [
            {
                'nombre': 'Martillo de Acero 16 oz',
                'precio': 12.50,
                'stock': 25,
                'stock_minimo': 5,
                'descripcion': 'Martillo de acero con mango de madera',
                'categoria_id': categorias[0].id
            },
            {
                'nombre': 'Destornillador Phillips #2',
                'precio': 3.75,
                'stock': 50,
                'stock_minimo': 10,
                'descripcion': 'Destornillador con punta Phillips número 2',
                'categoria_id': categorias[0].id
            },
            {
                'nombre': 'Taladro Percutor 1/2"',
                'precio': 85.00,
                'stock': 8,
                'stock_minimo': 2,
                'descripcion': 'Taladro percutor de 1/2 pulgada, 600W',
                'categoria_id': categorias[1].id
            },
            {
                'nombre': 'Cable THHN 12 AWG',
                'precio': 1.25,
                'stock': 200,
                'stock_minimo': 50,
                'descripcion': 'Cable eléctrico THHN calibre 12',
                'categoria_id': categorias[3].id
            },
            {
                'nombre': 'Pintura Látex Blanca 1 Gal',
                'precio': 18.50,
                'stock': 15,
                'stock_minimo': 5,
                'descripcion': 'Pintura látex interior blanca 1 galón',
                'categoria_id': categorias[5].id
            }
        ]
        
        for data in productos_data:
            producto = Producto(**data)
            producto.save()
        
        print("✅ Datos iniciales insertados exitosamente")
        print("👤 Usuarios creados:")
        print("   - admin@ferreteria.com (Administrador)")
        print("   - vendedor@ferreteria.com (Vendedor)")
        print("   - maria@ferreteria.com (Vendedor)")
        print("   ⚠️ IMPORTANTE: Cambia las contraseñas después del primer login")
        print(f"📦 Categorías creadas: {len(categorias_data)}")
        print(f"🏪 Proveedores creados: {len(proveedores_data)}")
        print(f"📋 Productos creados: {len(productos_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al insertar datos iniciales: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Configurar variables de entorno
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        # Crear tablas y datos iniciales
        create_tables()
        seed_data()
    
    port = int(os.environ.get('PORT', '5000'))
    print("🚀 Iniciando servidor Flask API...")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔗 API REST: http://localhost:{port}/api")
    print("📖 Docs: Ver README.md para endpoints disponibles")
    
    # Ejecutar en modo desarrollo
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
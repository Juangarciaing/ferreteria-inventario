#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar operaciones CRUD
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def get_token():
    """Obtener token de autenticación"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@ferreteria.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token') or data.get('token')
        print("✅ Token obtenido")
        return token
    else:
        print(f"❌ Error al obtener token: {response.status_code}")
        print(response.text)
        return None

def test_categorias_crud(token):
    """Probar CRUD de categorías"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("TESTING: CATEGORÍAS CRUD")
    print("="*80)
    
    # 1. CREATE
    print("\n1️⃣ CREATE - Crear nueva categoría")
    nueva_categoria = {
        "nombre": "Categoría de Prueba",
        "descripcion": "Esta es una categoría de prueba"
    }
    response = requests.post(f"{BASE_URL}/categorias", json=nueva_categoria, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        categoria_id = data.get('data', {}).get('id') or data.get('id')
        print(f"   ✅ Categoría creada con ID: {categoria_id}")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # 2. READ
    print("\n2️⃣ READ - Obtener categoría creada")
    response = requests.get(f"{BASE_URL}/categorias/{categoria_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   \u2705 Categor\u00eda obtenida correctamente")
        print(f"   Datos: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 3. UPDATE
    print("\n3️⃣ UPDATE - Actualizar categoría")
    actualizacion = {
        "nombre": "Categoría Actualizada",
        "descripcion": "Descripción actualizada"
    }
    response = requests.put(f"{BASE_URL}/categorias/{categoria_id}", json=actualizacion, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   \u2705 Categor\u00eda actualizada correctamente")
        print(f"   Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 4. DELETE
    print("\n4️⃣ DELETE - Eliminar categoría")
    response = requests.delete(f"{BASE_URL}/categorias/{categoria_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Categoría eliminada correctamente")
    else:
        print(f"   ❌ Error: {response.text}")

def test_productos_crud(token):
    """Probar CRUD de productos"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("TESTING: PRODUCTOS CRUD")
    print("="*80)
    
    # Obtener una categoría existente
    response = requests.get(f"{BASE_URL}/categorias", headers=headers)
    categorias = response.json()
    if isinstance(categorias, dict) and 'data' in categorias:
        categorias = categorias['data']
    categoria_id = categorias[0]['id'] if categorias else 1
    
    # 1. CREATE
    print("\n1️⃣ CREATE - Crear nuevo producto")
    nuevo_producto = {
        "nombre": "Producto de Prueba",
        "descripcion": "Descripción del producto de prueba",
        "precio": 99.99,
        "stock": 50,
        "stock_minimo": 10,
        "categoria_id": categoria_id
    }
    response = requests.post(f"{BASE_URL}/productos", json=nuevo_producto, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        producto_id = data.get('data', {}).get('id') or data.get('id')
        print(f"   ✅ Producto creado con ID: {producto_id}")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # 2. UPDATE
    print("\n2️⃣ UPDATE - Actualizar producto")
    actualizacion = {
        "nombre": "Producto Actualizado",
        "precio": 149.99,
        "stock": 75
    }
    response = requests.put(f"{BASE_URL}/productos/{producto_id}", json=actualizacion, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   \u2705 Producto actualizado correctamente")
        print(f"   Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 3. DELETE
    print("\n3️⃣ DELETE - Eliminar producto")
    response = requests.delete(f"{BASE_URL}/productos/{producto_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Producto eliminado correctamente")
    else:
        print(f"   ❌ Error: {response.text}")

def test_proveedores_crud(token):
    """Probar CRUD de proveedores"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("TESTING: PROVEEDORES CRUD")
    print("="*80)
    
    # 1. CREATE
    print("\n1️⃣ CREATE - Crear nuevo proveedor")
    nuevo_proveedor = {
        "nombre": "Proveedor de Prueba",
        "contacto": "Juan Pérez",
        "telefono": "555-1234",
        "email": "prueba@proveedor.com",
        "direccion": "Calle Falsa 123"
    }
    response = requests.post(f"{BASE_URL}/proveedores", json=nuevo_proveedor, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        proveedor_id = data.get('data', {}).get('id') or data.get('id')
        print(f"   ✅ Proveedor creado con ID: {proveedor_id}")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # 2. UPDATE
    print("\n2️⃣ UPDATE - Actualizar proveedor")
    actualizacion = {
        "contacto": "María García",
        "telefono": "555-5678"
    }
    response = requests.put(f"{BASE_URL}/proveedores/{proveedor_id}", json=actualizacion, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   \u2705 Proveedor actualizado correctamente")
        print(f"   Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 3. DELETE
    print("\n3️⃣ DELETE - Eliminar proveedor")
    response = requests.delete(f"{BASE_URL}/proveedores/{proveedor_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Proveedor eliminado correctamente")
    else:
        print(f"   ❌ Error: {response.text}")

def test_utf8_categorias(token):
    """Probar que las categorías con UTF-8 funcionan correctamente"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("TESTING: UTF-8 EN CATEGORÍAS")
    print("="*80)
    
    print("\n📋 Obteniendo todas las categorías...")
    response = requests.get(f"{BASE_URL}/categorias", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        categorias = response.json()
        if isinstance(categorias, dict) and 'data' in categorias:
            categorias = categorias['data']
        
        print(f"\n   ✅ Total de categorías: {len(categorias)}")
        print("\n   Categorías con caracteres especiales:")
        for cat in categorias:
            nombre = cat['nombre']
            if any(c in nombre for c in 'áéíóúñÁÉÍÓÚÑ'):
                print(f"      • ID {cat['id']}: {nombre}")
    else:
        print(f"   ❌ Error: {response.text}")

def main():
    print("🚀 Iniciando pruebas CRUD del sistema de ferretería")
    print("="*80)
    
    # Obtener token
    token = get_token()
    if not token:
        print("❌ No se pudo obtener el token. Abortando pruebas.")
        return
    
    # Ejecutar pruebas
    try:
        test_utf8_categorias(token)
        test_categorias_crud(token)
        test_productos_crud(token)
        test_proveedores_crud(token)
        
        print("\n" + "="*80)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

# Diagnóstico de Módulos - Sistema de Inventario Ferretería

## 📋 Estado General del Sistema

### ✅ Backend (Puerto 5000)
- **Estado**: Funcionando correctamente
- **Base de datos**: MySQL conectada (ferreteria_db)
- **Autenticación**: JWT funcionando
- **Endpoints**: Todos los endpoints responden correctamente (HTTP 200)

### ✅ Frontend (Puerto 5173)
- **Estado**: Servidor Vite funcionando
- **Hot Module Reload**: Activo
- **Compilación**: Sin errores críticos

---

## 🔍 Análisis por Módulo

### 1. 🏠 Dashboard (`/dashboard`)
**Estado**: ⚠️ Parcialmente funcional

**Problemas identificados**:
- El dashboard carga pero no muestra datos
- Los métodos del API ahora están completos en `api.ts`

**Métodos API utilizados** (todos implementados):
- ✅ `getDashboardStats()` → `/dashboard/stats`
- ✅ `getVentasRecientes(5)` → `/dashboard/ventas-recientes?limit=5`
- ✅ `getVentasPorDia(7)` → `/dashboard/ventas-por-dia?dias=7`
- ✅ `getProductosMasVendidosDashboard(5, 30)` → `/dashboard/productos-mas-vendidos?limit=5`
- ✅ `getStockCritico()` → `/dashboard/stock-critico`
- ✅ `getActividadReciente(10)` → `/dashboard/actividad-reciente?limit=10`

**Solución**:
1. Refresca el navegador (Ctrl+F5)
2. Verifica en la consola del navegador (F12) si hay errores
3. Verifica en la pestaña Network si las llamadas API regresan datos

---

### 2. 📦 Productos (`/productos`)
**Estado**: ✅ Debería funcionar

**Hook utilizado**: `useProductos()`

**Métodos API utilizados** (todos implementados):
- ✅ `getProductos()` → `/productos`
- ✅ `createProducto()` → `POST /productos`
- ✅ `updateProducto()` → `PUT /productos/:id`
- ✅ `deleteProducto()` → `DELETE /productos/:id`
- ✅ `searchProductos()` → `/productos/search?q=...`

**Datos del backend**:
- 5 productos en la base de datos
- Categorías: 12 disponibles
- Proveedores: 3 disponibles

---

### 3. 🏷️ Categorías (`/categorias`)
**Estado**: ✅ Debería funcionar

**Hook utilizado**: `useCategorias()`

**Métodos API utilizados** (todos implementados):
- ✅ `getCategorias()` → `/categorias`
- ✅ `createCategoria()` → `POST /categorias`
- ✅ `updateCategoria()` → `PUT /categorias/:id`
- ✅ `deleteCategoria()` → `DELETE /categorias/:id`

**Datos del backend**:
- 12 categorías disponibles

---

### 4. 🏢 Proveedores (`/proveedores`)
**Estado**: ✅ Debería funcionar

**Hook utilizado**: `useProveedores()`

**Métodos API utilizados** (todos implementados):
- ✅ `getProveedores()` → `/proveedores`
- ✅ `createProveedor()` → `POST /proveedores`
- ✅ `updateProveedor()` → `PUT /proveedores/:id`
- ✅ `deleteProveedor()` → `DELETE /proveedores/:id`

**Datos del backend**:
- 3 proveedores disponibles

---

### 5. 💰 Ventas (`/ventas`)
**Estado**: ✅ Debería funcionar

**Hook utilizado**: `useVentas()`

**Métodos API utilizados** (todos implementados):
- ✅ `getVentas()` → `/ventas`
- ✅ `createVenta()` → `POST /ventas`
- ✅ `deleteVenta()` → `DELETE /ventas/:id` ⬅️ **RECIÉN AGREGADO**
- ✅ `getProductos()` → Necesario para listar productos disponibles

**Datos del backend**:
- Sistema de ventas con detalles de productos
- Actualización automática de stock
- Generación de PDFs

---

### 6. 🛒 Compras (`/compras`)
**Estado**: ✅ Debería funcionar

**Hook utilizado**: `useCompras()`

**Métodos API utilizados** (todos implementados):
- ✅ `getCompras()` → `/compras`
- ✅ `createCompra()` → `POST /compras`
- ✅ `getProductos()` → Necesario para listar productos
- ✅ `getProveedores()` → Necesario para listar proveedores

**Datos del backend**:
- Sistema de compras funcional
- Actualización automática de stock

---

### 7. 👥 Usuarios (`/usuarios`)
**Estado**: ✅ Debería funcionar

**Hook utilizado**: `useUsuarios()`

**Métodos API utilizados** (todos implementados):
- ✅ `getUsuarios()` → `/usuarios` (solo admin)
- ✅ `createUsuario()` → `POST /usuarios`
- ✅ `updateUsuario()` → `PUT /usuarios/:id`
- ✅ `deleteUsuario()` → `DELETE /usuarios/:id`

**Datos del backend**:
- 3 usuarios: 1 admin + 2 vendedores
- Control de roles: admin/vendedor

---

### 8. ⚠️ Alertas de Stock (`/alertas-stock`)
**Estado**: ✅ Debería funcionar

**Métodos API utilizados**:
- ✅ `getProductosStockBajo()` → `/productos/stock-bajo` ⬅️ **RECIÉN AGREGADO ALIAS**

**Funcionalidad**:
- Muestra productos con stock <= stock_minimo
- Separa productos agotados (stock = 0)
- Permite navegar a compras para reabastecimiento

---

### 9. 📊 Reportes (`/reportes`)
**Estado**: ✅ Debería funcionar

**Métodos API utilizados** (todos implementados):
- ✅ `getVentasPorFecha()` → `/reportes/ventas-por-fecha?fecha_inicio=...&fecha_fin=...`
- ✅ `getProductosMasVendidos()` → `/reportes/productos-mas-vendidos?limit=...`

---

## 🔧 Cambios Realizados en `api.ts`

### Métodos agregados recientemente:
1. **`getProductosStockBajo()`** - Alias de `getProductosBajoStock()`
2. **`deleteVenta(id)`** - Para anular ventas
3. **`getVentasPorDia(dias)`** - Ventas por día para dashboard
4. **`getProductosMasVendidosDashboard(limit, dias)`** - Top productos vendidos
5. **`getStockCritico()`** - Productos con stock crítico
6. **`getActividadReciente(limit)`** - Actividad reciente (ventas y compras)

---

## 🎯 Pasos Siguientes para Diagnosticar

### 1. Refrescar el Navegador
```
Presiona Ctrl+F5 o Cmd+Shift+R
```
Esto recargará completamente el frontend con los nuevos cambios.

### 2. Abrir la Consola del Navegador
```
Presiona F12 → Pestaña "Console"
```
Busca errores en rojo que indiquen problemas de JavaScript.

### 3. Ver Llamadas de Red
```
F12 → Pestaña "Network"
```
- Filtra por "Fetch/XHR"
- Recarga la página
- Verifica que las llamadas a `/api/...` retornen HTTP 200
- Haz clic en cada llamada para ver la respuesta

### 4. Verificar Autenticación
```
F12 → Pestaña "Application" → "Local Storage"
```
Verifica que existan:
- `token`: Token JWT válido
- `user`: Información del usuario

---

## ⚡ Comandos Rápidos

### Reiniciar Backend
```powershell
cd "e:\Sotfware 2\ferreteria-inventario-main\ferreteria-inventario-main"
py run_api.py
```

### Reiniciar Frontend
```powershell
cd "e:\Sotfware 2\ferreteria-inventario-main\Ferreteria"
npm run dev
```

### Ver Logs del Backend
El backend muestra en consola:
- Todas las consultas SQL ejecutadas
- Errores de la API
- Respuestas HTTP (200, 404, 500, etc.)

---

## 🐛 Problemas Conocidos

1. **Dashboard no muestra datos**: Puede ser que los endpoints devuelvan arrays vacíos si no hay datos en la BD
2. **Pantallas en blanco**: Verifica la consola del navegador para errores de JavaScript
3. **"Error al cargar"**: Puede indicar problema de autenticación o red

---

## 📝 Credenciales de Prueba

```
Admin:
Email: admin@ferreteria.com
Password: admin123

Vendedor:
Email: vendedor@ferreteria.com
Password: vendedor123
```

---

## 🎓 URLs del Sistema

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000/api
- **Documentación API**: http://localhost:5000/api/docs (si está habilitado)

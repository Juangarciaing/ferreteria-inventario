# 🏪 Sistema de Inventario Ferretería

Sistema completo de gestión de inventario para ferretería con backend Python/Flask (Clean Architecture) y frontend React/TypeScript.

## ✨ **NUEVAS CARACTERÍSTICAS**

- ✅ **Clean Architecture** - Backend con arquitectura limpia (4 capas)
- ✅ **Logging Profesional** - Sistema de logs automático (app.log, error.log, access.log)
- ✅ **Paginación Inteligente** - Manejo eficiente de grandes volúmenes de datos
- ✅ **Health Checks** - 4 endpoints de monitoreo y diagnóstico
- ✅ **API REST Completa** - 46 endpoints con documentación
- ✅ **Frontend Moderno** - React 18 + TypeScript + TailwindCSS

## 🚀 **INSTALACIÓN RÁPIDA**

### **Prerrequisitos:**
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### **1. Backend (Python/Flask)**

```bash
# Clonar e instalar dependencias
cd ferreteria-inventario-main
pip install -r requirements.txt

# Inicializar base de datos
python init_db.py

# Ejecutar servidor
python run_api.py
```

**Servidor disponible en:** `http://localhost:5000`

### **2. Frontend (React/TypeScript)**

```bash
# En otra terminal, ir al directorio frontend
cd ../Ferreteria

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

**Frontend disponible en:** `http://localhost:5173`

## 🏥 **HEALTH CHECKS**

Verificar estado del sistema:

```bash
# Check básico
GET http://localhost:5000/api/health

# Check detallado (BD, CPU, memoria, disco)
GET http://localhost:5000/api/health/detailed

# Estadísticas del sistema
GET http://localhost:5000/api/health/stats

# Ping simple
GET http://localhost:5000/api/health/ping
```

## 👤 **USUARIOS DE PRUEBA**

| Email | Contraseña | Rol |
|-------|------------|-----|
| admin@ferreteria.com | admin123 | Administrador |
| vendedor@ferreteria.com | vendedor123 | Vendedor |
| maria@ferreteria.com | maria123 | Vendedor |

## 📋 **FUNCIONALIDADES**

### **Backend (API REST)**
- ✅ Autenticación JWT
- ✅ Gestión de usuarios (CRUD)
- ✅ Gestión de productos (CRUD)
- ✅ Gestión de categorías (CRUD)
- ✅ Gestión de proveedores (CRUD)
- ✅ Gestión de ventas y compras
- ✅ Reportes y estadísticas
- ✅ Control de stock y alertas
- ✅ Búsqueda de productos

### **Frontend (React/TypeScript)**
- ✅ Dashboard con estadísticas
- ✅ Gestión de productos
- ✅ Gestión de categorías
- ✅ Gestión de proveedores
- ✅ Gestión de usuarios (admin)
- ✅ Sistema de ventas
- ✅ Sistema de compras
- ✅ Reportes y gráficos
- ✅ Alertas de stock bajo
- ✅ Búsqueda y filtros

## 🗄️ **BASE DE DATOS**

### **Configuración por defecto:**
- **Host:** localhost
- **Puerto:** 3306
- **Usuario:** root
- **Contraseña:** root
- **Base de datos:** ferreteria_db

### **Personalizar configuración:**
Editar `app/config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:contraseña@host:puerto/ferreteria_db'
```

## 🔧 **ESTRUCTURA DEL PROYECTO**

```
ferreteria-inventario-main/
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   ├── controllers/     # Controladores de negocio
│   ├── services/        # Servicios de aplicación
│   ├── repositories/    # Capa de acceso a datos
│   ├── utils/           # Utilidades
│   ├── api_routes.py    # Rutas principales de API
│   ├── api_additional.py # Rutas adicionales
│   └── config.py        # Configuración
├── Ferreteria/          # Frontend React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas principales
│   │   ├── hooks/       # Hooks personalizados
│   │   ├── contexts/    # Contextos React
│   │   ├── lib/         # Cliente API
│   │   └── types/       # Tipos TypeScript
│   └── package.json
├── init_db.py           # Script de inicialización
├── run_api.py           # Servidor principal
└── requirements.txt      # Dependencias Python

```

## 📊 **ENDPOINTS DE API**

### **Autenticación**
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión

### **Productos**
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto (admin)
- `PUT /api/productos/{id}` - Actualizar producto (admin)
- `DELETE /api/productos/{id}` - Eliminar producto (admin)
- `GET /api/productos/search?q={query}` - Buscar productos
- `GET /api/productos/stock-bajo` - Productos con stock bajo

### **Categorías**
- `GET /api/categorias` - Listar categorías
- `POST /api/categorias` - Crear categoría (admin)
- `PUT /api/categorias/{id}` - Actualizar categoría (admin)
- `DELETE /api/categorias/{id}` - Eliminar categoría (admin)

### **Proveedores**
- `GET /api/proveedores` - Listar proveedores
- `POST /api/proveedores` - Crear proveedor (admin)
- `PUT /api/proveedores/{id}` - Actualizar proveedor (admin)
- `DELETE /api/proveedores/{id}` - Eliminar proveedor (admin)

### **Ventas**
- `GET /api/ventas` - Listar ventas
- `POST /api/ventas` - Crear venta

### **Compras**
- `GET /api/compras` - Listar compras
- `POST /api/compras` - Crear compra

### **Dashboard**
- `GET /api/dashboard/stats` - Estadísticas generales
- `GET /api/dashboard/ventas-recientes` - Ventas recientes

### **Reportes**
- `GET /api/reportes/ventas-por-fecha` - Ventas por rango de fechas
- `GET /api/reportes/productos-mas-vendidos` - Productos más vendidos

## 🛠️ **DESARROLLO**

### **Backend:**
```bash
# Modo desarrollo con recarga automática
export FLASK_ENV=development
python run_api.py
```

### **Frontend:**
```bash
# Modo desarrollo con hot reload
npm run dev

# Construir para producción
npm run build

# Preview de producción
npm run preview
```

## 🐛 **SOLUCIÓN DE PROBLEMAS**

### **Error de conexión a MySQL:**
1. Verificar que MySQL esté ejecutándose
2. Verificar credenciales en `app/config.py`
3. Ejecutar `python init_db.py` para crear la base de datos

### **Error de CORS:**
- El backend ya tiene CORS configurado para `localhost:5173`
- Verificar que el frontend esté en el puerto correcto

### **Error de autenticación:**
- Verificar que el usuario exista en la base de datos
- Usar las credenciales de prueba proporcionadas

## 📝 **NOTAS TÉCNICAS**

- **Backend:** Flask + SQLAlchemy + PyMySQL + JWT
- **Frontend:** React + TypeScript + Tailwind CSS + Vite
- **Base de datos:** MySQL 8.0+
- **Autenticación:** JWT tokens
- **CORS:** Configurado para desarrollo local

## 🤝 **CONTRIBUCIÓN**

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 **LICENCIA**

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.
# 📂 Sistema de Inventario para Ferretería

Sistema completo de gestión de inventario desarrollado con **React + TypeScript** (frontend) y **Flask + MySQL** (backend).

## 🚀 Características Principales

### 👤 **Gestión de Usuarios**
- Login con JWT
- Roles diferenciados (Admin/Vendedor)
- Control de acceso por endpoints

### 📦 **Gestión de Inventario**
- CRUD completo de productos
- Categorías organizadas
- Control de stock mínimo
- Alertas de stock bajo
- Códigos de barras

### 🏪 **Gestión de Proveedores**
- Registro completo de proveedores
- Historial de compras
- Rating de proveedores
- Condiciones de pago

### 💰 **Sistema de Ventas**
- Registro de ventas con múltiples productos
- Cálculo automático de totales
- Historial completo
- Actualización automática de stock

### 📊 **Reportes y Analytics**
- Dashboard con métricas en tiempo real
- Reportes de ventas por fecha
- Productos más vendidos
- Estadísticas de inventario

## 🛠️ Tecnologías Utilizadas

### Frontend
- **React 18** + **TypeScript**
- **Tailwind CSS** para estilos
- **React Router** para navegación
- **React Hook Form** para formularios
- **Recharts** para gráficos
- **React Hot Toast** para notificaciones

### Backend
- **Flask** + **SQLAlchemy**
- **MySQL** como base de datos
- **JWT** para autenticación
- **Flask-CORS** para cross-origin
- **PyMySQL** para conexión DB

## 📋 Prerrequisitos

- **Node.js** (v18+)
- **Python** (v3.11+)
- **MySQL** (v8.0+)

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd ferreteria-inventario
```

### 2. Configurar Backend
```bash
cd ferreteria-inventario-main

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
# Crear base de datos 'ferreteria_db' en MySQL
python init_db.py

# Iniciar servidor
python run_api.py
```

### 3. Configurar Frontend
```bash
cd ../Ferreteria

# Instalar dependencias
npm install

# Iniciar aplicación
npm run dev
```

### 4. Acceder al Sistema
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## 👤 Usuarios de Prueba

- **Admin**: `admin@ferreteria.com` / `admin123`
- **Vendedor**: `vendedor@ferreteria.com` / `vendedor123`

## 📚 Documentación API

### Autenticación
```bash
POST /api/auth/login
POST /api/auth/logout
```

### Productos
```bash
GET    /api/productos
POST   /api/productos
PUT    /api/productos/{id}
DELETE /api/productos/{id}
GET    /api/productos/search?q=query
GET    /api/productos/stock-bajo
```

### Categorías
```bash
GET    /api/categorias
POST   /api/categorias
PUT    /api/categorias/{id}
DELETE /api/categorias/{id}
```

### Proveedores
```bash
GET    /api/proveedores
POST   /api/proveedores
PUT    /api/proveedores/{id}
DELETE /api/proveedores/{id}
```

### Ventas
```bash
GET    /api/ventas
POST   /api/ventas
```

### Dashboard y Reportes
```bash
GET /api/dashboard/stats
GET /api/dashboard/ventas-recientes
GET /api/reportes/ventas-por-fecha
GET /api/reportes/productos-mas-vendidos
```

## 📊 Estructura del Proyecto

```
ferreteria-inventario/
├── ferreteria-inventario-main/     # Backend Flask
│   ├── app/
│   │   ├── controllers/            # Controladores API
│   │   ├── models/                 # Modelos SQLAlchemy
│   │   ├── repositories/           # Capa de datos
│   │   ├── services/               # Lógica de negocio
│   │   └── utils/                  # Utilidades
│   ├── init_db.py                  # Inicialización DB
│   ├── requirements.txt            # Dependencias Python
│   └── run_api.py                  # Punto de entrada
└── Ferreteria/                     # Frontend React
    ├── src/
    │   ├── components/             # Componentes reutilizables
    │   ├── pages/                  # Páginas principales
    │   ├── contexts/               # Contextos React
    │   ├── hooks/                  # Hooks personalizados
    │   ├── lib/                    # Utilidades y API client
    │   └── types/                  # Tipos TypeScript
    └── package.json                # Dependencias Node.js
```

## 🔧 Configuración Personalizada

### Variables de Entorno (Opcional)
Crear `.env` en la raíz del backend:
```env
SECRET_KEY=tu-clave-secreta
DATABASE_URL=mysql+pymysql://usuario:password@localhost/ferreteria_db
JWT_SECRET_KEY=tu-jwt-secret
```

### Base de Datos
Modificar `app/config.py` si usas credenciales diferentes:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/ferreteria_db'
```

## 🚀 Despliegue en Producción

### Backend
```bash
# Usar Gunicorn para producción
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run_api:app
```

### Frontend
```bash
# Construir para producción
npm run build

# Servir archivos estáticos con nginx o similar
```

## 📈 Próximas Mejoras

- [ ] Códigos de barras con scanner
- [ ] Notificaciones push
- [ ] Backup automático
- [ ] Integración con POS
- [ ] App móvil
- [ ] Reportes avanzados en PDF
- [ ] Dashboard en tiempo real

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu-email@ejemplo.com

---

⭐ **¡Dale una estrella si este proyecto te fue útil!** ⭐
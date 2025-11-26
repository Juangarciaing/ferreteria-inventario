# Ferretería - Frontend (Vite + React + TypeScript)

## Requisitos
- Node.js 18+
- Backend Flask corriendo y accesible (local o remoto)

## Configuración
1. Copiar `.env.example` a `.env` y ajustar si tu API no es local:

```
VITE_API_BASE_URL=http://localhost:5000/api
```

2. Instalar dependencias:
```
npm install
```

3. Ejecutar en desarrollo:
```
npm run dev
```

4. Abrir la URL indicada por Vite (por defecto `http://localhost:5173`).

## Autenticación
- Iniciar sesión con:
  - admin@ferreteria.com / admin123 (Administrador)
  - vendedor@ferreteria.com / vendedor123 (Vendedor)

El token JWT se almacena en `localStorage` y se inyecta automáticamente en las peticiones.

## Endpoints usados (principales)
- Productos: `/productos`, `/productos/search`, `/productos/stock-bajo`
- Categorías: `/categorias`
- Proveedores: `/proveedores`
- Compras: `/compras`
- Ventas: `/ventas`
- Dashboard: `/dashboard/stats`
- Usuarios: `/usuarios` (solo admin para mutaciones)

## Notas
- Si cambias el origen del frontend, configura CORS en el backend con `CORS_ORIGINS`.
- `VITE_API_BASE_URL` debe incluir el sufijo `/api`.

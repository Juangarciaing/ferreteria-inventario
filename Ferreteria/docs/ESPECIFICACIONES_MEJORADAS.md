# PROYECTO: SISTEMA DE CONTROL DE INVENTARIO - FERRETERÍA (MEJORADO)
===============================================
Documento: Especificación detallada de módulos y conexiones - VERSIÓN MEJORADA
Propósito: Describir qué hace cada módulo, cómo se conectan, rutas/funciones principales,
modelos de datos, reglas de negocio, validaciones, tests recomendados y tecnologías.

**TECNOLOGÍA ACTUALIZADA**: React + TypeScript + Supabase + Tailwind CSS

## ÍNDICE MEJORADO
1. Resumen ejecutivo
2. Arquitectura general (componentes y conexiones)
3. Listado de módulos y descripción detallada (responsabilidades, modelos, endpoints, templates)
   3.1 Autenticación (auth) ✅
   3.2 Usuarios (user management) ✅
   3.3 Categorías ✅
   3.4 Productos ✅
   3.5 **NUEVO: Proveedores**
   3.6 Compras / Ingreso de stock ✅
   3.7 Ventas ✅
   3.8 DetalleVenta (líneas de venta) ✅
   3.9 **NUEVO: Devoluciones y Ajustes de inventario**
   3.10 **NUEVO: Descuentos y Promociones**
   3.11 Reportes y gráficos ✅
   3.12 Alertas de stock ✅
   3.13 Dashboard ✅
   3.14 Exportar (PDF / Excel) ✅
   3.15 Búsqueda / filtros ✅
   3.16 **NUEVO: Códigos de barras y QR**
   3.17 **NUEVO: Notificaciones en tiempo real**
   3.18 **NUEVO: Auditoría y logs de actividad**
   3.19 API REST completa ✅
   3.20 Tests, Migrations, Config y utilidades ✅
4. Flujos clave mejorados (secuencia)
5. Reglas de negocio y validaciones comunes
6. **NUEVO: Performance y optimización**
7. Consideraciones de seguridad y despliegue
8. **NUEVO: Integración con servicios externos**
9. Pruebas unitarias recomendadas (casos por módulo)
10. **NUEVO: Métricas de negocio y KPIs**
11. **NUEVO: Backup y recuperación de desastres**
12. Recomendaciones finales (imágenes, gráficos, UI)
13. **NUEVO: Roadmap y funcionalidades futuras**
14. Apéndice: snippets útiles

-------------------------
## 1. RESUMEN EJECUTIVO MEJORADO
-------------------------
Aplicación web moderna (React + TypeScript + Supabase) para gestionar inventario y ventas de una ferretería. Soporta:

**Funcionalidades Core:**
- Autenticación con roles avanzados (admin, vendedor, supervisor, auditor)
- CRUD completo de productos, categorías y proveedores
- Gestión avanzada de stock con códigos de barras
- Registro de compras, ventas y devoluciones
- Control automático de stock con múltiples niveles de alerta
- Sistema de descuentos y promociones
- Reportes avanzados con gráficos interactivos
- Auditoría completa de todas las operaciones
- Notificaciones en tiempo real
- Exportación múltiple (PDF, Excel, CSV)
- API REST completa para integraciones

**Tecnologías:**
- Frontend: React 18 + TypeScript + Tailwind CSS + React Router
- Backend: Supabase (PostgreSQL + Auth + Storage + Edge Functions)
- UI: Headless UI + Hero Icons + Chart.js/Recharts
- Testing: Vitest + React Testing Library
- Deploy: Vercel/Netlify (Frontend) + Supabase (Backend)

-------------------------
## 2. ARQUITECTURA GENERAL MEJORADA
-------------------------
**Componentes:**
- Frontend: React SPA con routing, state management (Zustand/Redux Toolkit)
- Backend: Supabase (PostgreSQL + Row Level Security + Edge Functions)
- Real-time: Supabase Realtime para notificaciones
- Storage: Supabase Storage para archivos (imágenes, PDFs)
- Auth: Supabase Auth con providers múltiples
- API: RESTful + GraphQL opcional

**Patrones de diseño:**
- Component-based architecture
- Custom hooks para lógica reutilizable
- Context API para estado global
- Lazy loading para componentes
- Error boundaries para manejo de errores
- Suspense para loading states

-------------------------
## 3. MÓDULOS MEJORADOS (DETALLE)
-------------------------

### 3.5 NUEVO: PROVEEDORES
**Responsabilidad:**
- CRUD de proveedores/distribuidores
- Historial de compras por proveedor
- Evaluación de desempeño de proveedores

**Modelo:**
```typescript
interface Proveedor {
  id: string;
  nombre: string;
  contacto: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  rut_ruc?: string;
  condiciones_pago: 'contado' | 'credito_30' | 'credito_60';
  descuento_default?: number;
  estado: 'activo' | 'inactivo';
  rating?: number; // 1-5 estrellas
  notas?: string;
  created_at: string;
  updated_at: string;
}
```

**Rutas:**
- `/proveedores` - Lista y gestión
- `/proveedores/nuevo` - Crear proveedor
- `/proveedores/:id/editar` - Editar
- `/proveedores/:id/historial` - Historial de compras

**Tests:**
- CRUD completo de proveedores
- Validación de datos únicos (RUT/RUC)
- Filtros por estado y rating

### 3.9 NUEVO: DEVOLUCIONES Y AJUSTES DE INVENTARIO
**Responsabilidad:**
- Registrar devoluciones de clientes
- Ajustes de inventario (mermas, robos, correcciones)
- Productos defectuosos

**Modelos:**
```typescript
interface Devolucion {
  id: string;
  venta_id?: string; // Si es devolución de venta
  tipo: 'devolucion_cliente' | 'ajuste_inventario' | 'producto_defectuoso';
  usuario_id: string;
  motivo: string;
  total: number;
  fecha: string;
  estado: 'pendiente' | 'procesada' | 'rechazada';
  detalles: DetalleDevolucion[];
}

interface DetalleDevolucion {
  id: string;
  devolucion_id: string;
  producto_id: string;
  cantidad: number;
  tipo_ajuste: 'incremento' | 'decremento';
  precio_unitario: number;
  subtotal: number;
}
```

### 3.10 NUEVO: DESCUENTOS Y PROMOCIONES
**Responsabilidad:**
- Crear y gestionar descuentos
- Aplicar promociones automáticamente
- Cupones de descuento

**Modelo:**
```typescript
interface Descuento {
  id: string;
  nombre: string;
  tipo: 'porcentaje' | 'monto_fijo';
  valor: number;
  tipo_aplicacion: 'producto' | 'categoria' | 'total_venta';
  producto_ids?: string[];
  categoria_ids?: string[];
  monto_minimo?: number;
  fecha_inicio: string;
  fecha_fin: string;
  uso_maximo?: number;
  uso_actual: number;
  codigo_cupon?: string;
  estado: 'activo' | 'inactivo';
}
```

### 3.16 NUEVO: CÓDIGOS DE BARRAS Y QR
**Responsabilidad:**
- Generar códigos de barras para productos
- Escanear códigos para ventas rápidas
- Etiquetas de precios con códigos

**Funcionalidades:**
- Generación automática de códigos EAN-13
- Escáner web usando cámara
- Impresión de etiquetas
- Búsqueda rápida por código

**Tecnologías:**
- `react-barcode-generator` para generación
- `react-qr-scanner` para escaneo
- `jspdf` para etiquetas PDF

### 3.17 NUEVO: NOTIFICACIONES EN TIEMPO REAL
**Responsabilidad:**
- Alertas de stock bajo
- Notificaciones de ventas grandes
- Cambios de precios
- Login de usuarios

**Implementación:**
- Supabase Realtime subscriptions
- Toast notifications (react-hot-toast)
- Push notifications (opcional)
- Email notifications para admins

### 3.18 NUEVO: AUDITORÍA Y LOGS DE ACTIVIDAD
**Responsabilidad:**
- Registrar todas las acciones críticas
- Historial de cambios en productos/precios
- Seguimiento de accesos

**Modelo:**
```typescript
interface AuditoriaLog {
  id: string;
  usuario_id: string;
  accion: string; // 'crear_producto', 'actualizar_precio', etc.
  tabla_afectada: string;
  registro_id: string;
  datos_anteriores?: any;
  datos_nuevos?: any;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
}
```

-------------------------
## 6. NUEVO: PERFORMANCE Y OPTIMIZACIÓN
-------------------------

**Frontend:**
- Code splitting por rutas
- Lazy loading de componentes pesados
- Memoización con React.memo y useMemo
- Virtualized lists para tablas grandes
- Image optimization y lazy loading
- Service Workers para cache

**Backend/Database:**
- Índices optimizados en Supabase
- Paginación server-side
- Queries optimizadas con joins eficientes
- Cache con Redis (si necesario)
- Compresión de respuestas

**Métricas a monitorear:**
- First Contentful Paint < 2s
- Largest Contentful Paint < 4s
- Time to Interactive < 5s
- Query execution time < 100ms

-------------------------
## 8. NUEVO: INTEGRACIÓN CON SERVICIOS EXTERNOS
-------------------------

**Pagos:**
- Stripe/PayPal para pagos online
- Integración con POS físicos

**Contabilidad:**
- Export a sistemas como QuickBooks
- Facturación electrónica (según país)

**Logística:**
- APIs de shipping (FedEx, DHL)
- Tracking de envíos

**Marketing:**
- Email marketing (Mailchimp, SendGrid)
- WhatsApp Business API
- Google Analytics para métricas web

**ERP:**
- SAP, Oracle NetSuite integration
- APIs REST para sincronización

-------------------------
## 10. NUEVO: MÉTRICAS DE NEGOCIO Y KPIS
-------------------------

**Dashboard KPIs:**
- Margen de ganancia por producto/categoría
- Rotación de inventario (inventory turnover)
- Tiempo promedio de stock out
- Customer Lifetime Value (CLV)
- Average Order Value (AOV)
- Productos más/menos rentables
- Tendencias estacionales

**Alertas automáticas:**
- Stock crítico (< stock_minimo)
- Productos sin movimiento > 90 días
- Margen de ganancia < umbral
- Ventas diarias < promedio - 20%

-------------------------
## 11. NUEVO: BACKUP Y RECUPERACIÓN DE DESASTRES
-------------------------

**Estrategia de Backup:**
- Backup automático diario de base de datos
- Backup incremental cada 6 horas
- Almacenamiento en múltiples regiones
- Retention policy: 30 días diarios, 12 meses semanales

**Recuperación:**
- RPO (Recovery Point Objective): 6 horas máximo
- RTO (Recovery Time Objective): 2 horas máximo
- Plan de contingencia documentado
- Testing de recovery mensual

**Herramientas:**
- Supabase automatic backups
- AWS S3 para archivos estáticos
- Monitoring con uptimerobot

-------------------------
## 13. NUEVO: ROADMAP Y FUNCIONALIDADES FUTURAS
-------------------------

**Fase 2 (3-6 meses):**
- Módulo de facturación electrónica
- App móvil (React Native)
- Multi-tienda/sucursales
- Programa de fidelización

**Fase 3 (6-12 meses):**
- IA para predicción de demanda
- Chatbot para atención al cliente
- Integración con marketplaces (Amazon, ML)
- B2B portal para clientes mayoristas

**Fase 4 (12+ meses):**
- IoT para sensores de inventario
- Blockchain para trazabilidad
- AR para catálogo de productos
- ML para pricing dinámico

-------------------------
## REGLAS DE NEGOCIO MEJORADAS
-------------------------

**Nuevas reglas:**
1. **Pricing inteligente:** Alertar si el precio de venta < costo + margen mínimo
2. **Stock reservation:** Reservar stock durante proceso de venta (5 min timeout)
3. **Multi-warehouse:** Soporte para múltiples ubicaciones de almacén
4. **Lotes y vencimientos:** Control de productos con fecha de caducidad
5. **Unidades de medida:** Soporte para kg, litros, metros, etc.
6. **Conversiones:** Vender por unidad pero comprar por caja/pallet
7. **Precios dinámicos:** Por volumen, tipo de cliente, temporada
8. **Límites de crédito:** Control de ventas a crédito por cliente

**Validaciones avanzadas:**
- Validación de códigos de barras (algoritmo checksum)
- Detección de precios sospechosos (variación > 50%)
- Validación de stock negativo con excepciones autorizadas
- Control de descuentos máximos por usuario/rol

-------------------------
## COMPONENTES DE UI MEJORADOS
-------------------------

**Componentes reutilizables:**
```typescript
// DataTable con sorting, filtering, pagination
<DataTable
  data={productos}
  columns={columnas}
  searchable
  filterable
  exportable={['pdf', 'excel', 'csv']}
  actions={['edit', 'delete', 'duplicate']}
/>

// Dashboard widgets
<MetricCard
  title="Ventas del mes"
  value={ventasMes}
  trend={+5.2}
  icon={TrendingUpIcon}
  color="green"
/>

// Scanner component
<BarcodeScanner
  onScan={handleBarcodeScan}
  onError={handleScanError}
  constraints={{ facingMode: 'environment' }}
/>
```

**Responsive design:**
- Mobile-first approach
- Gestión de inventario desde tablet/móvil
- PWA para uso offline limitado
- Touch-friendly para POS

-------------------------
## TESTING STRATEGY MEJORADA
-------------------------

**Tipos de tests:**
1. **Unit tests:** Funciones puras, hooks, utils
2. **Integration tests:** Componentes + API calls
3. **E2E tests:** Flujos completos con Playwright
4. **Visual regression tests:** Chromatic para UI
5. **Performance tests:** Lighthouse CI
6. **Security tests:** OWASP ZAP scans

**Coverage goals:**
- Unit tests: 80%+ coverage
- Critical paths: 100% E2E coverage
- API endpoints: 100% integration tests

**Test data:**
- Factory functions para generar test data
- Seed data realista para desarrollo
- Cleanup automático entre tests

-------------------------
## DEPLOYMENT Y CI/CD MEJORADO
-------------------------

**Pipeline:**
```yaml
# GitHub Actions example
- name: Tests
  run: npm test -- --coverage
- name: Build
  run: npm run build
- name: Security scan
  run: npm audit --audit-level high
- name: Deploy to staging
  run: vercel deploy --prebuilt
- name: E2E tests on staging
  run: npm run test:e2e
- name: Deploy to production
  run: vercel deploy --prod --prebuilt
```

**Environments:**
- Development (local)
- Staging (auto-deploy from develop branch)
- Production (manual approval required)

**Monitoring:**
- Sentry for error tracking
- LogRocket for user sessions
- New Relic for APM
- Supabase dashboard for DB metrics

-------------------------
## CONCLUSIÓN
-------------------------

Este documento mejorado proporciona una base sólida para construir un sistema de inventario moderno, escalable y orientado al futuro. Las mejoras incluyen:

1. **Tecnología moderna:** React + Supabase stack
2. **Funcionalidades avanzadas:** Códigos de barras, auditoría, notificaciones
3. **Escalabilidad:** Performance, caching, optimización
4. **Mantenibilidad:** Testing exhaustivo, CI/CD, monitoreo
5. **Experiencia de usuario:** UI moderna, responsive, PWA
6. **Integración:** APIs para conectar con otros sistemas
7. **Inteligencia de negocio:** KPIs, reportes avanzados, predicciones

La implementación debe ser iterativa, comenzando con el MVP y agregando funcionalidades según prioridad de negocio y feedback de usuarios.
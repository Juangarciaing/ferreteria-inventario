# Plan Completo de Pruebas de Software
## Sistema de Inventario para Ferretería

---

## 📋 Índice
1. [Pruebas Unitarias](#1-pruebas-unitarias)
2. [Pruebas Funcionales e Integración](#2-pruebas-funcionales-e-integración)
3. [Pruebas de Rendimiento](#3-pruebas-de-rendimiento)
4. [Pruebas de Seguridad](#4-pruebas-de-seguridad)
5. [Pruebas de Usabilidad](#5-pruebas-de-usabilidad)
6. [Pruebas de Portabilidad](#6-pruebas-de-portabilidad)
7. [Métricas y Análisis Estático](#7-métricas-y-análisis-estático)
8. [Cronograma de Ejecución](#cronograma-de-ejecución)

---

## 1. Pruebas Unitarias

### 1.1 Backend (Python/Flask)

**Herramientas:**
- `pytest` - Framework de testing
- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocking
- `unittest.mock` - Simulación de dependencias

**Áreas a Probar:**

#### A. Modelos de Datos
```python
# tests/unit/test_models.py
- ✅ Creación de productos
- ✅ Validaciones de stock
- ✅ Relaciones entre modelos (FK)
- ✅ Métodos to_dict()
- ✅ Validaciones de precio
```

#### B. Servicios/Lógica de Negocio
```python
# tests/unit/test_services.py
- ✅ Cálculo de totales
- ✅ Actualización de stock
- ✅ Validación de stock mínimo
- ✅ Cálculo de precios con descuentos
- ✅ Generación de códigos de barras
```

#### C. Utilidades
```python
# tests/unit/test_utils.py
- ✅ Validadores de entrada
- ✅ Formateadores de datos
- ✅ Helpers de fecha
- ✅ Encriptación de contraseñas
```

**Comando de Ejecución:**
```bash
cd ferreteria-inventario-main
pytest tests/unit/ -v --cov=app --cov-report=html
```

**Cobertura Objetivo:** ≥ 80%

---

### 1.2 Frontend (React/TypeScript)

**Herramientas:**
- `Jest` - Framework de testing
- `React Testing Library` - Testing de componentes
- `@testing-library/user-event` - Simulación de eventos

**Áreas a Probar:**

#### A. Componentes
```typescript
// src/__tests__/components/
- ✅ Renderizado de ProductoModal
- ✅ Validación de formularios
- ✅ Componentes de búsqueda
- ✅ Paginación
- ✅ Filtros
```

#### B. Hooks Personalizados
```typescript
// src/__tests__/hooks/
- ✅ useProductos - CRUD operaciones
- ✅ useCategorias
- ✅ useAuth - Autenticación
- ✅ useNotifications
```

#### C. Utilidades
```typescript
// src/__tests__/utils/
- ✅ Formateadores de precio
- ✅ Validadores de formularios
- ✅ Helpers de fecha
```

**Comando de Ejecución:**
```bash
cd Ferreteria
npm test -- --coverage
```

**Cobertura Objetivo:** ≥ 70%

---

## 2. Pruebas Funcionales e Integración

### 2.1 Pruebas de API (Backend)

**Herramientas:**
- `pytest` con fixtures
- `requests` - Cliente HTTP
- Base de datos de prueba

**Casos de Prueba:**

#### A. Autenticación y Autorización
```python
# tests/integration/test_auth_integration.py
✅ Login exitoso
✅ Login con credenciales incorrectas
✅ Acceso a rutas protegidas
✅ Verificación de tokens JWT
✅ Refresh de tokens
✅ Control de roles (admin vs usuario)
```

#### B. CRUD de Productos
```python
# tests/integration/test_productos_integration.py
✅ Crear producto
✅ Listar productos con paginación
✅ Actualizar producto
✅ Eliminar producto
✅ Búsqueda de productos
✅ Filtrado por categoría
✅ Productos con stock bajo
```

#### C. Gestión de Compras
```python
# tests/integration/test_compras_integration.py
✅ Registrar compra
✅ Actualización automática de stock
✅ Editar compra
✅ Eliminar compra
✅ Listar compras con filtros
```

#### D. Gestión de Ventas
```python
# tests/integration/test_ventas_integration.py
✅ Registrar venta
✅ Descuento de stock automático
✅ Validación de stock disponible
✅ Cálculo de totales
✅ Ventas por período
```

**Comando de Ejecución:**
```bash
pytest tests/integration/ -v --maxfail=1
```

---

### 2.2 Pruebas End-to-End (E2E)

**Herramientas:**
- `Playwright` o `Cypress`
- `Selenium` (alternativa)

**Flujos Completos a Probar:**

#### A. Flujo de Usuario Administrador
```javascript
// e2e/admin-flow.spec.ts
✅ Login como admin
✅ Crear nueva categoría
✅ Crear nuevo producto
✅ Registrar compra
✅ Actualizar stock
✅ Generar reporte
✅ Logout
```

#### B. Flujo de Usuario Regular
```javascript
// e2e/user-flow.spec.ts
✅ Login como usuario
✅ Buscar producto
✅ Registrar venta
✅ Ver historial de ventas
✅ Exportar datos
✅ Logout
```

#### C. Flujo de Gestión de Inventario
```javascript
// e2e/inventory-flow.spec.ts
✅ Verificar productos con stock bajo
✅ Registrar compra para reponer stock
✅ Verificar actualización de stock
✅ Editar información de producto
✅ Ver alertas de stock mínimo
```

**Instalación de Playwright:**
```bash
cd Ferreteria
npm install -D @playwright/test
npx playwright install
```

**Comando de Ejecución:**
```bash
npx playwright test
npx playwright test --ui  # Modo interactivo
```

---

## 3. Pruebas de Rendimiento

### 3.1 Pruebas de Carga

**Herramientas:**
- `Locust` (Python) - Testing de carga
- `Apache JMeter` (alternativa)
- `k6` (alternativa moderna)

**Escenarios a Probar:**

#### A. Carga Normal
```python
# performance/locustfile.py
- 10-50 usuarios simultáneos
- Operaciones: Login, listar productos, buscar
- Duración: 10 minutos
- Objetivo: < 500ms respuesta promedio
```

#### B. Carga Pico
```python
- 100-200 usuarios simultáneos
- Operaciones mixtas (CRUD)
- Duración: 5 minutos
- Objetivo: < 2s respuesta promedio
- < 1% tasa de error
```

#### C. Prueba de Estrés
```python
- Incremento gradual hasta 500 usuarios
- Identificar punto de quiebre
- Medir recuperación del sistema
```

**Archivo de Configuración:**
```python
# performance/locustfile.py
from locust import HttpUser, task, between

class InventarioUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "admin@ferreteria.com",
            "password": "admin123"
        })
        self.token = response.json()["token"]
    
    @task(3)
    def listar_productos(self):
        self.client.get("/api/productos", 
            headers={"Authorization": f"Bearer {self.token}"})
    
    @task(2)
    def buscar_producto(self):
        self.client.get("/api/productos/search?q=tornillo",
            headers={"Authorization": f"Bearer {self.token}"})
    
    @task(1)
    def crear_venta(self):
        self.client.post("/api/ventas", json={
            "detalles": [{"producto_id": 1, "cantidad": 2}]
        }, headers={"Authorization": f"Bearer {self.token}"})
```

**Ejecución:**
```bash
pip install locust
locust -f performance/locustfile.py --host=http://localhost:5000
# Abrir http://localhost:8089
```

---

### 3.2 Pruebas de Frontend (Lighthouse)

**Herramientas:**
- `Lighthouse` - Auditoría de rendimiento
- `WebPageTest`

**Métricas a Medir:**
```
✅ First Contentful Paint (FCP) < 1.8s
✅ Largest Contentful Paint (LCP) < 2.5s
✅ Time to Interactive (TTI) < 3.8s
✅ Cumulative Layout Shift (CLS) < 0.1
✅ Total Blocking Time (TBT) < 300ms
```

**Comando:**
```bash
npm install -g lighthouse
lighthouse http://localhost:5173 --view
```

---

## 4. Pruebas de Seguridad

### 4.1 Análisis de Vulnerabilidades

**Herramientas:**
- `Bandit` - Python security linter
- `Safety` - Dependencias vulnerables
- `npm audit` - Frontend
- `OWASP ZAP` - Pentesting

**Pruebas a Realizar:**

#### A. Backend
```bash
# Análisis estático de código
pip install bandit
bandit -r app/ -f json -o security/bandit-report.json

# Verificar dependencias
pip install safety
safety check --json > security/safety-report.json

# SQL Injection
pytest tests/security/test_sql_injection.py
```

#### B. Frontend
```bash
# Auditoría de dependencias
npm audit
npm audit fix

# Análisis de XSS
npm install -D eslint-plugin-security
```

#### C. Autenticación y Autorización
```python
# tests/security/test_auth_security.py
✅ Tokens JWT seguros
✅ Expiración de sesiones
✅ Protección de rutas
✅ Validación de roles
✅ Rate limiting
✅ CORS configurado correctamente
```

#### D. Inyección SQL
```python
# tests/security/test_sql_injection.py
✅ Pruebas con inputs maliciosos
✅ Validación de parámetros
✅ Uso de prepared statements
```

#### E. XSS (Cross-Site Scripting)
```typescript
// tests/security/test_xss.spec.ts
✅ Sanitización de inputs
✅ Escape de HTML
✅ Content Security Policy
```

---

### 4.2 Penetration Testing

**Herramientas:**
- `OWASP ZAP` - Automated scanner
- `Burp Suite Community`

**Checklist OWASP Top 10:**
```
✅ A01:2021 – Broken Access Control
✅ A02:2021 – Cryptographic Failures
✅ A03:2021 – Injection
✅ A04:2021 – Insecure Design
✅ A05:2021 – Security Misconfiguration
✅ A06:2021 – Vulnerable Components
✅ A07:2021 – Authentication Failures
✅ A08:2021 – Software and Data Integrity
✅ A09:2021 – Security Logging Failures
✅ A10:2021 – Server-Side Request Forgery
```

---

## 5. Pruebas de Usabilidad

### 5.1 Heurísticas de Nielsen

**Evaluación Manual:**

```
✅ Visibilidad del estado del sistema
   - Feedback al guardar/eliminar
   - Loading states
   - Notificaciones claras

✅ Coincidencia con el mundo real
   - Terminología del dominio
   - Iconos intuitivos

✅ Control y libertad del usuario
   - Confirmación antes de eliminar
   - Botón de cancelar en formularios
   - Breadcrumbs

✅ Consistencia y estándares
   - Diseño uniforme
   - Nomenclatura consistente

✅ Prevención de errores
   - Validaciones en tiempo real
   - Límites en inputs numéricos

✅ Reconocimiento vs recuerdo
   - Placeholders informativos
   - Tooltips en campos complejos

✅ Flexibilidad y eficiencia
   - Búsqueda rápida
   - Filtros avanzados
   - Shortcuts de teclado

✅ Diseño estético y minimalista
   - Sin información innecesaria
   - Jerarquía visual clara

✅ Ayudar a reconocer y recuperarse de errores
   - Mensajes de error descriptivos
   - Sugerencias de corrección

✅ Ayuda y documentación
   - Tooltips contextuales
   - README completo
```

---

### 5.2 Pruebas de Accesibilidad (A11y)

**Herramientas:**
- `axe DevTools` - Chrome extension
- `Lighthouse` - Accessibility audit
- `WAVE` - Web accessibility evaluator

**Estándares WCAG 2.1:**

```
Nivel A (Mínimo):
✅ Contraste de colores adecuado
✅ Textos alternativos en imágenes
✅ Navegación por teclado
✅ Labels en formularios

Nivel AA (Recomendado):
✅ Contraste 4.5:1 para texto normal
✅ Tamaño de área de click ≥ 44x44px
✅ Orden de foco lógico
✅ Mensajes de error accesibles

Nivel AAA (Avanzado):
✅ Contraste 7:1
✅ Sin timeout automático
```

**Comando:**
```bash
npm install -D @axe-core/react
# En desarrollo, se mostrarán warnings en consola
```

---

### 5.3 Pruebas con Usuarios Reales

**Protocolo:**

1. **Reclutamiento:** 5-10 usuarios objetivo (dueños de ferreterías, empleados)
2. **Tareas:**
   - Registrar un producto nuevo
   - Buscar un producto existente
   - Realizar una venta
   - Generar un reporte
3. **Métricas:**
   - Tiempo de completación
   - Tasa de éxito
   - Satisfacción (escala 1-5)
   - Comentarios cualitativos

---

## 6. Pruebas de Portabilidad

### 6.1 Compatibilidad de Navegadores

**Navegadores a Probar:**
```
✅ Chrome 120+ (Windows, macOS, Linux)
✅ Firefox 121+ (Windows, macOS, Linux)
✅ Safari 17+ (macOS, iOS)
✅ Edge 120+ (Windows)
```

**Herramientas:**
- `BrowserStack` - Testing en la nube
- `Selenium Grid` - Testing local
- Manual testing

---

### 6.2 Responsividad

**Dispositivos/Resoluciones:**
```
✅ Desktop: 1920x1080, 1366x768, 1440x900
✅ Tablet: 768x1024 (iPad), 1024x768 (landscape)
✅ Mobile: 375x667 (iPhone), 360x640 (Android)
```

**Chrome DevTools:**
```bash
# Probar en diferentes viewports
# F12 > Toggle device toolbar (Ctrl+Shift+M)
```

---

### 6.3 Compatibilidad de Sistemas Operativos

**Backend:**
```
✅ Windows 10/11 + Python 3.9+
✅ macOS 12+ + Python 3.9+
✅ Ubuntu 20.04/22.04 + Python 3.9+
```

**Frontend:**
```
✅ Node.js 18+ en todos los OS
✅ Build reproducible
```

---

### 6.4 Bases de Datos

**Pruebas:**
```
✅ MySQL 8.0 (producción)
✅ MySQL 5.7 (retrocompatibilidad)
✅ MariaDB 10.6+ (alternativa)
```

---

## 7. Métricas y Análisis Estático

### 7.1 Backend (Python)

**Herramientas:**

#### A. Pylint
```bash
pip install pylint
pylint app/ --output-format=json > metrics/pylint-report.json
```

**Métricas:**
- Score objetivo: ≥ 8.0/10
- Convenciones PEP 8
- Complejidad ciclomática < 10

#### B. Radon
```bash
pip install radon
radon cc app/ -a -nb  # Complejidad ciclomática
radon mi app/          # Índice de mantenibilidad
```

**Objetivos:**
- Complejidad: A-B (≤ 10)
- Mantenibilidad: A-B (≥ 20)

#### C. SonarQube
```bash
sonar-scanner \
  -Dsonar.projectKey=ferreteria-inventario \
  -Dsonar.sources=app \
  -Dsonar.host.url=http://localhost:9000
```

**Métricas de Calidad:**
```
✅ Cobertura de código: ≥ 80%
✅ Duplicación de código: < 3%
✅ Deuda técnica: < 5%
✅ Code smells: 0 critical, < 10 major
✅ Bugs: 0 critical, 0 major
✅ Vulnerabilidades: 0
```

---

### 7.2 Frontend (TypeScript/React)

**Herramientas:**

#### A. ESLint
```bash
npm run lint
npm run lint -- --fix
```

**Configuración:**
```json
{
  "rules": {
    "complexity": ["error", 15],
    "max-lines-per-function": ["warn", 100],
    "max-depth": ["error", 4]
  }
}
```

#### B. TypeScript Compiler
```bash
npx tsc --noEmit
```

**Métricas:**
- 0 errores de tipo
- Strict mode habilitado

#### C. Bundle Size
```bash
npm run build
npm install -g bundlesize
bundlesize
```

**Objetivos:**
```
✅ Bundle principal: < 500 KB
✅ Vendor bundle: < 1 MB
✅ Lazy loaded chunks: < 200 KB cada uno
```

#### D. SonarQube Frontend
```bash
sonar-scanner \
  -Dsonar.projectKey=ferreteria-frontend \
  -Dsonar.sources=src \
  -Dsonar.typescript.lcov.reportPaths=coverage/lcov.info
```

---

### 7.3 Análisis de Dependencias

**Backend:**
```bash
pip list --outdated
pip-audit  # Vulnerabilidades
```

**Frontend:**
```bash
npm outdated
npm audit
npx depcheck  # Dependencias no usadas
```

---

## Cronograma de Ejecución

### Sprint de Testing (2 semanas)

**Semana 1: Testing Funcional**
```
Día 1-2: Pruebas Unitarias
  - Backend: Modelos y servicios
  - Frontend: Componentes y hooks

Día 3-4: Pruebas de Integración
  - API endpoints
  - Flujos de datos completos

Día 5: Pruebas E2E
  - Flujos principales
  - Casos críticos
```

**Semana 2: Testing No Funcional**
```
Día 1: Pruebas de Rendimiento
  - Locust (carga)
  - Lighthouse (frontend)

Día 2: Pruebas de Seguridad
  - Bandit/Safety
  - OWASP ZAP

Día 3: Pruebas de Usabilidad
  - Heurísticas de Nielsen
  - Accesibilidad

Día 4: Métricas y Análisis
  - SonarQube
  - Linters
  - Reportes de cobertura

Día 5: Correcciones y Re-testing
  - Fix de bugs encontrados
  - Validación final
```

---

## Comandos Rápidos

### Ejecutar Todas las Pruebas

**Backend:**
```bash
cd ferreteria-inventario-main

# Pruebas unitarias + integración + cobertura
pytest -v --cov=app --cov-report=html --cov-report=term

# Solo pruebas unitarias
pytest tests/unit/ -v

# Solo pruebas de integración
pytest tests/integration/ -v

# Con reporte detallado
pytest --html=report.html --self-contained-html
```

**Frontend:**
```bash
cd Ferreteria

# Todas las pruebas
npm test -- --coverage --watchAll=false

# Solo componentes
npm test -- --testPathPattern=components

# Solo hooks
npm test -- --testPathPattern=hooks

# Con UI interactiva
npm test -- --watch
```

**Análisis Estático:**
```bash
# Backend
pylint app/
bandit -r app/
safety check

# Frontend
npm run lint
npm run type-check
npm audit
```

---

## Reportes y Documentación

### Generación de Reportes

1. **Cobertura de Código:**
   - Backend: `htmlcov/index.html`
   - Frontend: `coverage/lcov-report/index.html`

2. **Seguridad:**
   - `security/bandit-report.json`
   - `security/safety-report.json`

3. **Rendimiento:**
   - Locust: `http://localhost:8089`
   - Lighthouse: `lighthouse-report.html`

4. **SonarQube:**
   - Dashboard: `http://localhost:9000`

---

## Criterios de Aceptación

### Para Pasar a Producción:

```
✅ Cobertura de código ≥ 80% (backend) y ≥ 70% (frontend)
✅ 0 vulnerabilidades críticas
✅ 0 bugs críticos
✅ Todas las pruebas E2E pasando
✅ Score SonarQube ≥ A
✅ Rendimiento: P95 < 2s
✅ Accesibilidad WCAG 2.1 AA
✅ Compatibilidad en navegadores principales
✅ Sin dependencias desactualizadas críticas
```

---

## Herramientas Adicionales Recomendadas

1. **CI/CD Integration:**
   - GitHub Actions
   - GitLab CI
   - Jenkins

2. **Monitoring:**
   - Sentry (error tracking)
   - New Relic (APM)
   - LogRocket (session replay)

3. **Documentation:**
   - Swagger/OpenAPI (API docs)
   - Storybook (componentes UI)

---

## Contacto y Soporte

Para dudas sobre las pruebas:
- Documentación: `README.md`
- Tests existentes: `tests/` y `src/__tests__/`
- Configuración: `pytest.ini` y `jest.config.js`

---

**Última actualización:** Noviembre 26, 2025
**Versión:** 1.0

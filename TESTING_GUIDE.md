# 🧪 Guía de Pruebas - Sistema Inventario Ferretería

## 📋 Índice
- [Configuración Rápida](#configuración-rápida)
- [Ejecutar Pruebas](#ejecutar-pruebas)
- [Base de Datos Temporal](#base-de-datos-temporal)
- [Integración con SonarCloud](#integración-con-sonarcloud)
- [Resolución de Problemas](#resolución-de-problemas)

---

## ⚡ Configuración Rápida

### 1. Instalar Dependencias

**Backend (Python):**
```bash
cd ferreteria-inventario-main
py -m pip install -r requirements.txt --user
py -m pip install pytest pytest-cov --user
```

**Frontend (Node.js):**
```bash
cd Ferreteria
npm install
```

---

## 🚀 Ejecutar Pruebas

### Opción 1: Script Automático (Recomendado)
```bash
# Ejecuta todas las pruebas con BD temporal
run_tests_simple.bat
```

Este script:
- ✅ Usa base de datos SQLite en memoria (no afecta MySQL)
- ✅ Genera reportes de cobertura HTML y XML
- ✅ Usa comando `py` en lugar de `python`
- ✅ Instala dependencias automáticamente si faltan

### Opción 2: Manual

**Backend:**
```bash
cd ferreteria-inventario-main
py -m pytest tests/ -v --cov=app --cov-report=html --cov-report=xml
```

**Frontend:**
```bash
cd Ferreteria
npm test -- --coverage --watchAll=false
```

### Opción 3: Solo un Archivo
```bash
# Backend - un archivo específico
cd ferreteria-inventario-main
py -m pytest tests/test_api.py -v

# Backend - un test específico
py -m pytest tests/test_auth.py::TestAuth::test_login -v

# Frontend - un archivo específico
cd Ferreteria
npm test -- App.test.tsx
```

---

## 🗄️ Base de Datos Temporal

### ¿Por qué SQLite en memoria?

Las pruebas usan **SQLite en memoria** en lugar de MySQL por:
- ✅ **No afecta datos reales**: Tu base de datos de desarrollo queda intacta
- ✅ **Rápido**: 10-20x más rápido que MySQL
- ✅ **Aislado**: Cada test comienza con BD limpia
- ✅ **Sin configuración**: No requiere servidor de base de datos

### Configuración (ya implementada)

En `tests/conftest.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
```

### Fixtures Disponibles

```python
def test_ejemplo(client, auth_headers, sample_producto):
    """
    client: Cliente Flask de prueba
    auth_headers: Headers con token JWT
    sample_producto: Producto de ejemplo ya creado
    """
    response = client.get(f'/api/productos/{sample_producto["id"]}', 
                         headers=auth_headers)
    assert response.status_code == 200
```

**Fixtures disponibles:**
- `client` - Cliente Flask de prueba
- `auth_token` - Token JWT válido
- `auth_headers` - Headers con autenticación
- `sample_categoria` - Categoría de ejemplo
- `sample_producto` - Producto de ejemplo
- `sample_proveedor` - Proveedor de ejemplo

---

## ☁️ Integración con SonarCloud

### Configuración (ver SONARCLOUD_SETUP.md)

1. **Configurar GitHub Actions**: Ya creado en `.github/workflows/sonarcloud.yml`
2. **Agregar token**: GitHub Settings → Secrets → `SONAR_TOKEN`
3. **Actualizar sonar-project.properties**: Cambiar `projectKey` y `organization`

### Análisis Automático

Cada push o PR ejecuta automáticamente:
```
✓ Pruebas Backend (pytest)
✓ Pruebas Frontend (Jest)
✓ Cobertura de Código
✓ Análisis de Calidad (SonarCloud)
✓ Reporte de Vulnerabilidades
```

### Análisis Local

```bash
# 1. Configurar token (una sola vez)
setx SONAR_TOKEN "tu-token-aqui"

# 2. Ejecutar análisis
run_sonar_analysis.bat
```

Requisito: Instalar [SonarScanner](https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/)

---

## 📊 Reportes de Cobertura

### Backend
- **HTML**: `ferreteria-inventario-main/htmlcov/index.html`
- **XML** (para SonarCloud): `ferreteria-inventario-main/coverage.xml`
- **Terminal**: Muestra resumen al ejecutar pytest

### Frontend
- **HTML**: `Ferreteria/coverage/lcov-report/index.html`
- **LCOV** (para SonarCloud): `Ferreteria/coverage/lcov.info`
- **Terminal**: Muestra tabla de cobertura

### Abrir Reportes
```bash
# Backend
start ferreteria-inventario-main\htmlcov\index.html

# Frontend
start Ferreteria\coverage\lcov-report\index.html
```

---

## 🔧 Resolución de Problemas

### Error: "No module named pytest"
```bash
cd ferreteria-inventario-main
py -m pip install pytest pytest-cov --user
```

### Error: "Could not find platform independent libraries"
- Normal en Python 3.14, no afecta funcionalidad
- Usar `--user` flag: `py -m pip install ... --user`

### Error: "Acceso denegado" al instalar
```bash
# Usar flag --user
py -m pip install pytest pytest-cov --user
```

### Error: "npm test fails"
```bash
cd Ferreteria
# Limpiar e reinstalar
rm -rf node_modules package-lock.json
npm install
npm test
```

### Pruebas pasan localmente pero fallan en CI
- Verificar que `conftest.py` esté en `tests/` directorio
- Verificar rutas en `sonar-project.properties`
- Verificar que coverage.xml y lcov.info se generen

### Base de datos real se modifica durante tests
- Verificar que uses `client` fixture, no conexión directa
- Revisar que `conftest.py` esté configurado correctamente
- Cada test debe usar `SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'`

---

## 📈 Métricas de Calidad

### Umbrales Actuales

**Backend (pytest):**
- Cobertura mínima: ≥60% (configurado en `pytest.ini`)
- Meta recomendada: ≥80%

**Frontend (Jest):**
- Cobertura mínima: ≥70% (configurado en `jest.config.js`)
- Meta recomendada: ≥80%

**SonarCloud Quality Gate:**
- Cobertura nuevas líneas: ≥80%
- Bugs críticos: 0
- Vulnerabilidades: 0
- Code Smells críticos: 0
- Rating: ≥A

---

## 🎯 Tipos de Pruebas

### Pruebas Unitarias
- **Ubicación**: `tests/unit/`
- **Objetivo**: Probar modelos y funciones aisladas
- **Ejemplo**: `test_models.py`

### Pruebas de Integración
- **Ubicación**: `tests/integration/`
- **Objetivo**: Probar flujos completos de API
- **Ejemplo**: `test_api_flows.py`

### Pruebas de API
- **Ubicación**: `tests/test_api.py`, `test_auth.py`, etc.
- **Objetivo**: Probar endpoints específicos
- **Usa**: Cliente Flask + fixtures

### Pruebas Frontend
- **Ubicación**: `Ferreteria/src/__tests__/`
- **Framework**: Jest + React Testing Library
- **Ejemplo**: `App.test.tsx`

---

## 🔐 Análisis de Seguridad

```bash
# Ejecutar análisis de seguridad completo
run_security_scan.bat
```

Incluye:
- **Bandit**: Escaneo de código Python
- **Safety**: Vulnerabilidades en dependencias Python
- **npm audit**: Vulnerabilidades en dependencias JavaScript

Reportes en: `ferreteria-inventario-main/security/`

---

## 📚 Comandos Útiles

```bash
# Ver ayuda de pytest
py -m pytest --help

# Ejecutar solo tests marcados
py -m pytest -m unit
py -m pytest -m integration

# Modo verboso con output completo
py -m pytest -v -s

# Parar en primer fallo
py -m pytest -x

# Ejecutar último test que falló
py -m pytest --lf

# Ver duración de tests
py -m pytest --durations=10

# Frontend: modo watch
cd Ferreteria
npm test

# Frontend: con cobertura
npm test -- --coverage

# Frontend: actualizar snapshots
npm test -- -u
```

---

## ✅ Checklist Pre-Commit

Antes de hacer commit, verificar:

- [ ] `run_tests_simple.bat` pasa todas las pruebas
- [ ] Cobertura ≥80% para código nuevo
- [ ] No hay errores de linting (`npm run lint`)
- [ ] No hay vulnerabilidades críticas (`npm audit`)
- [ ] Código formateado correctamente
- [ ] Tests nuevos para código nuevo
- [ ] Base de datos temporal usada (no MySQL)

---

## 🆘 Ayuda Adicional

- **Documentación pytest**: https://docs.pytest.org/
- **Documentación Jest**: https://jestjs.io/
- **SonarCloud**: Ver `SONARCLOUD_SETUP.md`
- **Plan de Pruebas Completo**: Ver `PLAN_PRUEBAS.md`

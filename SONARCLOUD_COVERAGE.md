# 🎯 Guía de Configuración de Cobertura para SonarCloud

## ✅ Estado Actual

Tu proyecto **YA ESTÁ CONFIGURADO** correctamente. Solo faltan estos pasos:

---

## 📝 Checklist de Configuración

### 1. ✅ Archivo sonar-project.properties
Ya está configurado con:
```properties
sonar.projectKey=Juangarciaing_ferreteria-inventario
sonar.organization=juangarciaing
sonar.python.coverage.reportPaths=ferreteria-inventario-main/coverage.xml
sonar.typescript.lcov.reportPaths=Ferreteria/coverage/lcov.info
```

### 2. ⚠️ Token de SonarCloud en GitHub

**DEBES HACER ESTO:**

1. **Generar Token en SonarCloud:**
   - Ve a https://sonarcloud.io
   - Click en tu avatar (esquina superior derecha)
   - **My Account** → **Security**
   - **Generate Tokens**
   - Name: `GitHub Actions`
   - Type: `User Token`
   - Click **Generate**
   - **COPIA EL TOKEN** (solo se muestra una vez)

2. **Agregar Token a GitHub:**
   - Ve a tu repositorio: https://github.com/Juangarciaing/ferreteria-inventario
   - Click en **Settings** (del repositorio, no tu cuenta)
   - En el menú izquierdo: **Secrets and variables** → **Actions**
   - Click en **New repository secret**
   - Name: `SONAR_TOKEN`
   - Secret: [pega el token que copiaste]
   - Click **Add secret**

### 3. ✅ Workflow de GitHub Actions
Ya está configurado en `.github/workflows/sonarcloud.yml`

### 4. ⚠️ Generar Reportes de Cobertura

**DEBES EJECUTAR ESTO ANTES DE HACER PUSH:**

```bash
# Opción 1: Script automático (RECOMENDADO)
generate_coverage.bat

# Opción 2: Manual
# Backend
cd ferreteria-inventario-main
py -m pytest tests/ --cov=app --cov-report=xml --cov-report=html

# Frontend
cd ..\Ferreteria
npm test -- --coverage --watchAll=false --passWithNoTests
```

Esto generará:
- ✅ `ferreteria-inventario-main/coverage.xml` (para backend)
- ✅ `Ferreteria/coverage/lcov.info` (para frontend)

---

## 🚀 Flujo de Trabajo Completo

### Primera Vez (Setup):

```bash
# 1. Generar reportes de cobertura
generate_coverage.bat

# 2. Verificar que se crearon los archivos
# Debe existir: ferreteria-inventario-main/coverage.xml
# Debe existir: Ferreteria/coverage/lcov.info

# 3. Commit y Push
git add .
git commit -m "Add test coverage reports"
git push origin main
```

### Cada Vez que Actualices el Código:

```bash
# 1. Hacer tus cambios
# 2. Generar cobertura
generate_coverage.bat

# 3. Push (GitHub Actions se ejecuta automáticamente)
git add .
git commit -m "Tu mensaje"
git push
```

---

## 📊 Cómo Ver los Resultados en SonarCloud

1. Ve a https://sonarcloud.io/dashboard?id=Juangarciaing_ferreteria-inventario
2. Después de cada push, verás:
   - **Overview**: Resumen general
   - **Coverage**: % de código cubierto por tests
   - **Issues**: Problemas encontrados
   - **Security**: Vulnerabilidades

3. En cada Pull Request de GitHub verás:
   - Comentario automático de SonarCloud
   - Estado del Quality Gate (✅ Passed / ❌ Failed)
   - Link directo al análisis

---

## 🔍 Verificar Configuración Actual

### Verificar Token en GitHub:
1. Ve a: https://github.com/Juangarciaing/ferreteria-inventario/settings/secrets/actions
2. Debe aparecer `SONAR_TOKEN` en la lista

### Verificar Proyecto en SonarCloud:
1. Ve a: https://sonarcloud.io/project/configuration?id=Juangarciaing_ferreteria-inventario
2. En **Analysis Method** debe decir: "GitHub Actions"

### Verificar Archivos de Cobertura:
```bash
# Ejecutar
generate_coverage.bat

# Verificar que existan:
dir ferreteria-inventario-main\coverage.xml
dir Ferreteria\coverage\lcov.info
```

---

## ⚠️ Solución de Problemas

### Problema: "Coverage is not being displayed"

**Causa**: Los archivos `coverage.xml` y `lcov.info` no se generan o no se encuentran.

**Solución**:
```bash
# 1. Generar manualmente
generate_coverage.bat

# 2. Verificar que existen
dir ferreteria-inventario-main\coverage.xml
dir Ferreteria\coverage\lcov.info

# 3. Verificar rutas en sonar-project.properties
# Deben coincidir exactamente con donde se generan
```

### Problema: "Analysis failed in GitHub Actions"

**Causa**: Token no configurado o inválido.

**Solución**:
1. Regenerar token en SonarCloud
2. Actualizar secret en GitHub
3. Re-ejecutar el workflow

### Problema: "Coverage shows 0%"

**Causa**: Tests no se ejecutan o fallan.

**Solución**:
```bash
# Backend
cd ferreteria-inventario-main
py -m pytest tests/ -v

# Frontend
cd Ferreteria
npm test
```

---

## 📋 Comandos Rápidos

```bash
# Ver estado de cobertura local
generate_coverage.bat

# Ver reporte HTML backend
start ferreteria-inventario-main\htmlcov\index.html

# Ver reporte HTML frontend
start Ferreteria\coverage\lcov-report\index.html

# Análisis local con SonarScanner (requiere instalación)
run_sonar_analysis.bat

# Ejecutar solo tests (sin cobertura)
cd ferreteria-inventario-main && py -m pytest tests/ -v
cd Ferreteria && npm test
```

---

## 🎯 Métricas Objetivo

Para pasar el Quality Gate de SonarCloud:

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Coverage | ≥80% | Generar primero |
| Bugs | 0 | Por verificar |
| Vulnerabilities | 0 | Por verificar |
| Code Smells | <5% | Por verificar |
| Duplications | <3% | Por verificar |
| Maintainability Rating | A | Por verificar |

---

## ✅ Resumen de Acción Inmediata

**LO QUE DEBES HACER AHORA:**

1. **Generar Token en SonarCloud** (solo una vez)
2. **Agregar SONAR_TOKEN a GitHub Secrets** (solo una vez)
3. **Ejecutar `generate_coverage.bat`** (cada vez)
4. **Push a GitHub** (automático después)

```bash
# Ejecutar ahora:
generate_coverage.bat

# Luego:
git add .
git commit -m "Configure SonarCloud coverage"
git push origin main

# Ver resultados en:
# https://sonarcloud.io/dashboard?id=Juangarciaing_ferreteria-inventario
```

---

## 🔗 Links Útiles

- **Tu Proyecto en SonarCloud**: https://sonarcloud.io/dashboard?id=Juangarciaing_ferreteria-inventario
- **Configuración del Proyecto**: https://sonarcloud.io/project/configuration?id=Juangarciaing_ferreteria-inventario
- **Tu Repositorio GitHub**: https://github.com/Juangarciaing/ferreteria-inventario
- **Secrets de GitHub**: https://github.com/Juangarciaing/ferreteria-inventario/settings/secrets/actions
- **Documentación SonarCloud**: https://docs.sonarcloud.io/

---

## 💡 Tip Pro

Agrega esto a tu `.gitignore` para no subir reportes de cobertura:

```
# Coverage reports (se generan en CI/CD)
coverage.xml
htmlcov/
.coverage
Ferreteria/coverage/
```

Los reportes se generarán automáticamente en GitHub Actions y se enviarán a SonarCloud. ✨

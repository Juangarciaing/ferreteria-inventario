# Configuración de SonarCloud para Sistema de Inventario

## 🚀 Configuración Inicial

### 1. Crear cuenta en SonarCloud
1. Ir a [https://sonarcloud.io](https://sonarcloud.io)
2. Hacer login con GitHub
3. Autorizar acceso a tu organización/repositorio

### 2. Importar Proyecto
1. En SonarCloud dashboard, click en "+" → "Analyze new project"
2. Seleccionar el repositorio: `ferreteria-inventario`
3. Click en "Set Up"
4. Elegir "With GitHub Actions" como método de análisis

### 3. Configurar Token
1. En SonarCloud: Account → Security → Generate Token
2. Copiar el token generado
3. En GitHub: Repository → Settings → Secrets and variables → Actions
4. Click "New repository secret"
   - Name: `SONAR_TOKEN`
   - Value: [pegar el token de SonarCloud]

### 4. Actualizar sonar-project.properties
Editar el archivo `sonar-project.properties` en la raíz del proyecto:

```properties
sonar.projectKey=TU-ORGANIZACION_ferreteria-inventario
sonar.organization=TU-ORGANIZACION
```

Reemplazar `TU-ORGANIZACION` con tu organización real de SonarCloud.

---

## 📊 Análisis Automático (GitHub Actions)

Una vez configurado, el análisis se ejecuta automáticamente en:
- ✅ Cada push a `main` o `develop`
- ✅ Cada Pull Request

El workflow `.github/workflows/sonarcloud.yml` se encarga de:
1. Ejecutar todas las pruebas backend (pytest)
2. Ejecutar todas las pruebas frontend (Jest)
3. Generar reportes de cobertura
4. Enviar resultados a SonarCloud
5. Subir reportes como artefactos

---

## 💻 Análisis Local

### Opción 1: Script Automático
```bash
# Configurar token (una sola vez)
setx SONAR_TOKEN "tu-token-aqui"

# Ejecutar análisis
run_sonar_analysis.bat
```

### Opción 2: Manual

#### Instalar SonarScanner
1. Descargar de: https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/
2. Extraer en `C:\sonar-scanner`
3. Agregar al PATH: `C:\sonar-scanner\bin`

#### Ejecutar Pruebas
```bash
# Backend
cd ferreteria-inventario-main
py -m pytest tests/ --cov=app --cov-report=xml

# Frontend
cd ..\Ferreteria
npm test -- --coverage --watchAll=false
```

#### Ejecutar Análisis
```bash
cd ..
sonar-scanner.bat -Dsonar.host.url=https://sonarcloud.io -Dsonar.token=TU_TOKEN
```

---

## 📈 Métricas en SonarCloud

### Quality Gate (Puerta de Calidad)
El proyecto debe cumplir:
- ✅ Cobertura de código ≥ 80% (nuevas líneas)
- ✅ 0 Bugs críticos
- ✅ 0 Vulnerabilidades
- ✅ 0 Security Hotspots
- ✅ Rating de Mantenibilidad ≥ A
- ✅ Duplicación de código < 3%

### Métricas Monitoreadas
- **Reliability**: Bugs y errores de código
- **Security**: Vulnerabilidades y hotspots
- **Maintainability**: Code smells y deuda técnica
- **Coverage**: % de código cubierto por tests
- **Duplications**: % de código duplicado

---

## 🔍 Ver Resultados

### En SonarCloud
1. Ir a https://sonarcloud.io
2. Seleccionar tu proyecto
3. Ver dashboard con:
   - Overview: Resumen general
   - Issues: Problemas encontrados
   - Security Hotspots: Puntos de seguridad
   - Measures: Métricas detalladas
   - Code: Navegador de código con anotaciones

### En GitHub
1. Ir a tu repositorio
2. Tab "Actions" para ver ejecuciones del workflow
3. Cada PR mostrará:
   - ✅/❌ Estado del Quality Gate
   - Link directo a SonarCloud
   - Comentarios automáticos con análisis

---

## 🛠️ Base de Datos Temporal

Las pruebas usan **SQLite en memoria** (`sqlite:///:memory:`) para:
- ✅ No afectar la base de datos de desarrollo
- ✅ Ejecutar pruebas múltiples veces sin conflictos
- ✅ Tests 10x más rápidos
- ✅ Cada test comienza con BD limpia

Configuración en `tests/conftest.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
```

---

## 📋 Checklist de Configuración

- [ ] Cuenta en SonarCloud creada
- [ ] Proyecto importado en SonarCloud
- [ ] Token generado en SonarCloud
- [ ] Secret `SONAR_TOKEN` configurado en GitHub
- [ ] `sonar-project.properties` actualizado con projectKey y organization
- [ ] Workflow `.github/workflows/sonarcloud.yml` committed
- [ ] Push a `main` para ejecutar primer análisis
- [ ] Verificar resultados en dashboard de SonarCloud

---

## 🚨 Troubleshooting

### Error: "Project not found"
- Verificar que `sonar.projectKey` coincida exactamente con SonarCloud
- Formato: `organizacion_nombre-proyecto`

### Error: "Unauthorized"
- Token inválido o expirado
- Regenerar token en SonarCloud
- Actualizar secret en GitHub

### Tests no se ejecutan
- Verificar que `pytest` esté instalado: `py -m pip install pytest pytest-cov`
- Verificar que `npm test` funcione localmente

### Cobertura en 0%
- Verificar rutas en `sonar-project.properties`:
  - `sonar.python.coverage.reportPaths=coverage.xml`
  - `sonar.javascript.lcov.reportPaths=Ferreteria/coverage/lcov.info`
- Los tests deben generar estos archivos

---

## 📚 Recursos

- [Documentación SonarCloud](https://docs.sonarcloud.io/)
- [SonarCloud GitHub Action](https://github.com/SonarSource/sonarcloud-github-action)
- [Configuración Python](https://docs.sonarcloud.io/advanced-setup/languages/python/)
- [Configuración JavaScript/TypeScript](https://docs.sonarcloud.io/advanced-setup/languages/javascript/)

@echo off
REM Script para analizar proyecto con SonarScanner localmente
echo ========================================
echo ANALISIS LOCAL CON SONARCLOUD
echo ========================================

echo.
echo PREREQUISITOS:
echo 1. Tener cuenta en SonarCloud (https://sonarcloud.io)
echo 2. Haber creado el proyecto en SonarCloud
echo 3. Tener el token de autenticacion
echo 4. Descargar SonarScanner desde: https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/
echo.

REM Verificar si existe el token
if "%SONAR_TOKEN%"=="" (
    echo ERROR: Variable de entorno SONAR_TOKEN no esta configurada
    echo.
    echo Para configurarla:
    echo    set SONAR_TOKEN=tu-token-aqui
    echo.
    echo O configurala permanentemente en Windows:
    echo    setx SONAR_TOKEN "tu-token-aqui"
    echo.
    pause
    exit /b 1
)

echo [1/3] Ejecutando pruebas con cobertura...
echo ----------------------------------------

REM Backend
echo - Backend tests...
cd ferreteria-inventario-main
py -m pytest tests/ --cov=app --cov-report=xml --cov-report=html --cov-report=term
cd ..

REM Frontend
echo - Frontend tests...
cd Ferreteria
call npm test -- --coverage --watchAll=false --passWithNoTests
cd ..

echo.
echo [2/3] Ejecutando analisis de seguridad...
echo ----------------------------------------
cd ferreteria-inventario-main
py -m bandit -r app/ -f json -o security\bandit-report.json
py -m safety check --json > security\safety-report.json
cd ..

echo.
echo [3/3] Ejecutando SonarScanner...
echo ----------------------------------------
echo IMPORTANTE: Editar sonar-project.properties con tu projectKey y organization
echo.

REM Ejecutar SonarScanner (debe estar en el PATH)
sonar-scanner.bat ^
  -Dsonar.host.url=https://sonarcloud.io ^
  -Dsonar.login=d2334ae6c62172c5b933e82f86438f1d500c5649

if %errorlevel% neq 0 (
    echo.
    echo ERROR: SonarScanner fallo
    echo.
    echo Posibles causas:
    echo 1. SonarScanner no esta instalado o no esta en el PATH
    echo 2. Token invalido
    echo 3. Configuracion incorrecta en sonar-project.properties
    echo.
    echo Para instalar SonarScanner:
    echo 1. Descargar de: https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/
    echo 2. Extraer en C:\sonar-scanner
    echo 3. Agregar C:\sonar-scanner\bin al PATH del sistema
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ANALISIS COMPLETADO
echo ========================================
echo.
echo Resultados disponibles en:
echo https://sonarcloud.io/dashboard?id=tu-organizacion_ferreteria-inventario
echo.
echo Reportes locales:
echo - Backend Coverage: ferreteria-inventario-main\htmlcov\index.html
echo - Frontend Coverage: Ferreteria\coverage\lcov-report\index.html
echo - Security Reports: ferreteria-inventario-main\security\
echo.
pause

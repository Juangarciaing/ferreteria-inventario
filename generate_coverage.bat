@echo off
REM Script para generar reportes de cobertura para SonarCloud
echo ========================================
echo GENERANDO REPORTES DE COBERTURA
echo ========================================

echo.
echo [1/2] Backend - Generando coverage.xml...
echo ----------------------------------------
cd ferreteria-inventario-main

REM Instalar dependencias si faltan
py -m pip show pytest-cov >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando pytest-cov...
    py -m pip install pytest-cov --user --quiet
)

REM Ejecutar tests con cobertura en formato XML
echo Ejecutando pruebas backend...
py -m pytest tests/ --cov=app --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term -v

if exist coverage.xml (
    echo ✓ Backend coverage.xml generado correctamente
    echo   Ubicacion: ferreteria-inventario-main\coverage.xml
) else (
    echo ✗ ERROR: No se genero coverage.xml
)

echo.
echo [2/2] Frontend - Generando lcov.info...
echo ----------------------------------------
cd ..\Ferreteria

REM Verificar node_modules
if not exist "node_modules\" (
    echo Instalando dependencias de Node.js...
    call npm install
)

REM Ejecutar tests con cobertura en formato LCOV
echo Ejecutando pruebas frontend...
call npm test -- --coverage --watchAll=false --passWithNoTests --coverageReporters=lcov --coverageReporters=text

if exist "coverage\lcov.info" (
    echo ✓ Frontend lcov.info generado correctamente
    echo   Ubicacion: Ferreteria\coverage\lcov.info
) else (
    echo ✗ ERROR: No se genero lcov.info
)

echo.
echo ========================================
echo VERIFICACION DE ARCHIVOS
echo ========================================
cd ..

echo.
echo Archivos necesarios para SonarCloud:
echo.

if exist "ferreteria-inventario-main\coverage.xml" (
    echo [✓] Backend: ferreteria-inventario-main\coverage.xml
) else (
    echo [✗] Backend: coverage.xml NO ENCONTRADO
)

if exist "Ferreteria\coverage\lcov.info" (
    echo [✓] Frontend: Ferreteria\coverage\lcov.info
) else (
    echo [✗] Frontend: lcov.info NO ENCONTRADO
)

echo.
echo ========================================
echo SIGUIENTE PASO
echo ========================================
echo.
echo Opciones:
echo 1. Subir a GitHub (automatico con Actions)
echo    git add .
echo    git commit -m "Add coverage reports"
echo    git push
echo.
echo 2. Analisis local (requiere SonarScanner instalado)
echo    run_sonar_analysis.bat
echo.
echo 3. Ver reportes HTML localmente:
echo    start ferreteria-inventario-main\htmlcov\index.html
echo    start Ferreteria\coverage\lcov-report\index.html
echo.
pause

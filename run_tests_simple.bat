@echo off
REM Script simplificado para ejecutar pruebas con base de datos temporal
REM Usa py en lugar de python y SQLite en memoria

echo ========================================
echo EJECUTANDO PRUEBAS CON BD TEMPORAL
echo ========================================

echo.
echo Configuracion:
echo - Backend: SQLite en memoria (no afecta MySQL)
echo - Frontend: Mock de API
echo - Comandos: 'py' en lugar de 'python'
echo.

echo [1/2] Pruebas Backend (pytest con BD temporal)...
echo ----------------------------------------
cd ferreteria-inventario-main

REM Verificar e instalar dependencias si es necesario
echo Verificando dependencias...
py -m pip show pytest >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando pytest y dependencias...
    py -m pip install pytest pytest-cov flask flask-sqlalchemy flask-jwt-extended flask-cors pymysql cryptography --user --quiet
)

echo Ejecutando pruebas backend...
py -m pytest tests/ -v --cov=app --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term-missing
set BACKEND_RESULT=%errorlevel%

if %BACKEND_RESULT% neq 0 (
    echo.
    echo ADVERTENCIA: Algunas pruebas backend fallaron o no se encontraron
    echo.
)

echo.
echo [2/2] Pruebas Frontend (Jest)...
echo ----------------------------------------
cd ..\Ferreteria

REM Verificar si node_modules existe
if not exist "node_modules\" (
    echo Instalando dependencias de Node.js...
    call npm install
)

echo Ejecutando pruebas frontend...
call npm test -- --coverage --watchAll=false --passWithNoTests
set FRONTEND_RESULT=%errorlevel%

echo.
echo ========================================
echo RESUMEN DE PRUEBAS
echo ========================================
echo Backend:  %BACKEND_RESULT% (0 = OK)
echo Frontend: %FRONTEND_RESULT% (0 = OK)
echo.
echo Reportes generados:
echo [Backend]
echo   - Cobertura HTML: ferreteria-inventario-main\htmlcov\index.html
echo   - Cobertura XML:  ferreteria-inventario-main\coverage.xml
echo [Frontend]
echo   - Cobertura HTML: Ferreteria\coverage\lcov-report\index.html
echo   - Cobertura LCOV: Ferreteria\coverage\lcov.info
echo.

if %BACKEND_RESULT% equ 0 if %FRONTEND_RESULT% equ 0 (
    echo ✓ TODAS LAS PRUEBAS PASARON
) else (
    echo ✗ ALGUNAS PRUEBAS FALLARON
)

echo.
echo NOTA: Las pruebas usan base de datos temporal (SQLite en memoria)
echo       No afectan la base de datos MySQL de desarrollo
echo.
pause

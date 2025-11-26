@echo off
REM Script para ejecutar análisis de seguridad
echo ========================================
echo ANALISIS DE SEGURIDAD
echo ========================================

echo.
echo [1/4] Instalando herramientas de seguridad...
echo ----------------------------------------
cd ferreteria-inventario-main
py -m pip install bandit safety --quiet

echo.
echo [2/4] Bandit - Escaneo de codigo Python...
echo ----------------------------------------
py -m bandit -r app/ -f json -o security\bandit-report.json
py -m bandit -r app/ -f txt
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Bandit encontro problemas potenciales
)

echo.
echo [3/4] Safety - Vulnerabilidades en dependencias Python...
echo ----------------------------------------
py -m safety check --json > security\safety-report.json
py -m safety check
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Safety encontro vulnerabilidades
)

echo.
echo [4/4] NPM Audit - Vulnerabilidades en dependencias JavaScript...
echo ----------------------------------------
cd ..\Ferreteria
call npm audit --json > ..\ferreteria-inventario-main\security\npm-audit.json
call npm audit
if %errorlevel% neq 0 (
    echo ADVERTENCIA: npm audit encontro vulnerabilidades
)

echo.
echo ========================================
echo ANALISIS DE SEGURIDAD COMPLETADO
echo ========================================
echo Reportes generados en: ferreteria-inventario-main\security\
echo - bandit-report.json (Python code scan)
echo - safety-report.json (Python dependencies)
echo - npm-audit.json (JavaScript dependencies)
echo.
pause

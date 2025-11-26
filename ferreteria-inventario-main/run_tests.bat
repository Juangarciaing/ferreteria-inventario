@echo off
REM Script para ejecutar todas las pruebas del proyecto
echo ========================================
echo EJECUTANDO SUITE COMPLETA DE PRUEBAS
echo ========================================

echo.
echo [1/3] Pruebas Backend (pytest)...
echo ----------------------------------------
cd ferreteria-inventario-main
py -m pytest -v --cov=app --cov-report=html --cov-report=xml --cov-report=term
if %errorlevel% neq 0 (
    echo FALLO: Pruebas backend fallaron
    pause
    exit /b 1
)

echo.
echo [2/3] Pruebas Frontend (Jest)...
echo ----------------------------------------
cd ..\Ferreteria
call npm test -- --coverage --watchAll=false
if %errorlevel% neq 0 (
    echo FALLO: Pruebas frontend fallaron
    pause
    exit /b 1
)

echo.
echo [3/3] Analisis Estatico (Linting)...
echo ----------------------------------------
echo - Backend: Pylint...
cd ..\ferreteria-inventario-main
py -m pylint app/ --output-format=text --reports=y > lint-backend.txt
echo   Reporte guardado en: lint-backend.txt

echo - Frontend: ESLint...
cd ..\Ferreteria
call npm run lint > lint-frontend.txt 2>&1
echo   Reporte guardado en: lint-frontend.txt

echo.
echo ========================================
echo PRUEBAS COMPLETADAS
echo ========================================
echo Reportes generados:
echo - Backend Coverage: ferreteria-inventario-main\htmlcov\index.html
echo - Frontend Coverage: Ferreteria\coverage\lcov-report\index.html
echo - Backend Linting: ferreteria-inventario-main\lint-backend.txt
echo - Frontend Linting: Ferreteria\lint-frontend.txt
echo.
pause

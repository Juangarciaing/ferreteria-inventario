@echo off
REM Script de instalación para Windows

echo 🚀 Iniciando instalación del Sistema de Inventario...

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado
    exit /b 1
)
echo ✅ Python instalado

REM Verificar Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado
    exit /b 1
)
echo ✅ Node.js instalado

REM Instalar backend
echo.
echo 🔧 Configurando backend...
cd ferreteria-inventario-main

echo ✅ Instalando dependencias de Python...
pip install -r requirements.txt

echo.
echo 🗄️ Configurando base de datos...
echo ⚠️  Asegúrate de que MySQL esté ejecutándose
set /p answer=¿Deseas ejecutar la inicialización de la base de datos? (y/n): 
if /i "%answer%"=="y" (
    python init_db.py
    if %errorlevel% equ 0 (
        echo ✅ Base de datos inicializada
    ) else (
        echo ❌ Error en base de datos
    )
)

cd ..

REM Instalar frontend
echo.
echo 🎨 Configurando frontend...
cd Ferreteria

echo ✅ Instalando dependencias de Node.js...
npm install

cd ..

REM Resumen
echo.
echo 🎉 ¡Instalación completada!
echo.
echo 🚀 Para ejecutar el sistema:
echo 1. Backend:  cd ferreteria-inventario-main ^&^& python run_api.py
echo 2. Frontend: cd Ferreteria ^&^& npm run dev
echo.
echo 🌐 URLs:
echo - Frontend: http://localhost:5173
echo - Backend:  http://localhost:5000
echo.
echo 👤 Usuarios de prueba:
echo - admin@ferreteria.com / admin123
echo - vendedor@ferreteria.com / vendedor123
echo.
echo ✅ ¡Sistema listo para usar!
pause
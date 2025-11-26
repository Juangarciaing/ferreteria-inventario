#!/bin/bash
# Script de instalación automática para Sistema de Inventario

echo "🚀 Iniciando instalación del Sistema de Inventario..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Función para mostrar mensajes
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar prerrequisitos
echo "📋 Verificando prerrequisitos..."

# Verificar Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_error "Python no está instalado"
    exit 1
fi
print_status "Python instalado"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js no está instalado"
    exit 1
fi
print_status "Node.js instalado"

# Verificar MySQL
if ! command -v mysql &> /dev/null; then
    print_warning "MySQL no detectado. Asegúrate de tenerlo instalado."
else
    print_status "MySQL detectado"
fi

# Instalar backend
echo ""
echo "🔧 Configurando backend..."
cd ferreteria-inventario-main

# Crear entorno virtual (opcional)
if [ ! -d "venv" ]; then
    print_status "Creando entorno virtual..."
    python -m venv venv 2>/dev/null || python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Instalar dependencias Python
print_status "Instalando dependencias de Python..."
pip install -r requirements.txt

# Configurar base de datos
echo ""
echo "🗄️ Configurando base de datos..."
print_warning "Asegúrate de que MySQL esté ejecutándose y tengas una base de datos 'ferreteria_db'"
read -p "¿Deseas ejecutar la inicialización automática de la base de datos? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python init_db.py
    if [ $? -eq 0 ]; then
        print_status "Base de datos inicializada correctamente"
    else
        print_error "Error al inicializar la base de datos"
        print_warning "Puedes ejecutar 'python init_db.py' manualmente después"
    fi
fi

cd ..

# Instalar frontend
echo ""
echo "🎨 Configurando frontend..."
cd Ferreteria

print_status "Instalando dependencias de Node.js..."
npm install

if [ $? -eq 0 ]; then
    print_status "Dependencias instaladas correctamente"
else
    print_error "Error al instalar dependencias del frontend"
fi

cd ..

# Resumen final
echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "🚀 Para ejecutar el sistema:"
echo "1. Backend:  cd ferreteria-inventario-main && python run_api.py"
echo "2. Frontend: cd Ferreteria && npm run dev"
echo ""
echo "🌐 URLs:"
echo "- Frontend: http://localhost:5173"
echo "- Backend:  http://localhost:5000"
echo ""
echo "👤 Usuarios de prueba:"
echo "- admin@ferreteria.com / admin123"
echo "- vendedor@ferreteria.com / vendedor123"
echo ""
print_status "¡Sistema listo para usar!"
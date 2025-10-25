#!/bin/bash

# Script para iniciar Asistente Tienda completo
# Incluye backend y frontend

echo "🏪 Asistente Tienda - Inicio Completo"
echo "====================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
show_message() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/app/main.py" ]; then
    show_error "No se encontró backend/app/main.py. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    show_error "No se encontró frontend/package.json. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

# Detener procesos existentes
show_info "Deteniendo procesos existentes..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# Verificar Python
if ! command -v python3 &> /dev/null; then
    show_error "Python3 no está instalado"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    show_error "Node.js no está instalado"
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    show_error "npm no está instalado"
    exit 1
fi

# Instalar dependencias del backend si es necesario
show_info "Verificando dependencias del backend..."
cd backend
if [ ! -d "venv" ]; then
    show_warning "No se encontró el entorno virtual. Creando..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    show_info "Instalando dependencias del backend..."
    pip install -r requirements.txt
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    if [ -f "env_enhanced.txt" ]; then
        show_warning "No se encontró .env. Copiando desde env_enhanced.txt..."
        cp env_enhanced.txt .env
        show_warning "IMPORTANTE: Configura tu OPENAI_API_KEY en backend/.env"
    else
        show_error "No se encontró archivo .env ni env_enhanced.txt"
        exit 1
    fi
fi

# Volver al directorio raíz
cd ..

# Instalar dependencias del frontend
show_info "Verificando dependencias del frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    show_info "Instalando dependencias del frontend..."
    npm install
fi

# Volver al directorio raíz
cd ..

# Función para iniciar backend
start_backend() {
    show_info "Iniciando backend de Asistente Tienda..."
    cd backend
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
    
    echo "🚀 Backend iniciando en http://localhost:8000"
    echo "📚 API Docs en http://localhost:8000/docs"
    echo "🏪 Asistente Tienda Backend"
    echo ""
    
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
}

# Función para iniciar frontend
start_frontend() {
    show_info "Iniciando frontend de Asistente Tienda..."
    cd frontend
    
    echo "🎨 Frontend iniciando en http://localhost:5173"
    echo "🏪 Asistente Tienda Frontend"
    echo ""
    
    npm run dev &
    FRONTEND_PID=$!
    cd ..
}

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    show_info "Deteniendo servidores..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true
    show_message "Servidores detenidos"
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

# Iniciar servicios
start_backend
sleep 3
start_frontend

# Mostrar información
echo ""
echo "🏪 Asistente Tienda - Servicios Iniciados"
echo "=========================================="
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "💬 Chat Mejorado: http://localhost:5173/enhanced-chat"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"
echo ""

# Esperar a que termine alguno de los procesos
wait

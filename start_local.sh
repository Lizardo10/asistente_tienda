#!/bin/bash
# Script para iniciar el proyecto en modo desarrollo local

echo "🚀 Iniciando proyecto en modo desarrollo local..."
echo "================================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[PASO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# 1. Configurar backend
print_step "Configurando backend..."
cd backend

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    print_step "Creando entorno virtual..."
    python -m venv .venv
fi

# Activar entorno virtual
print_step "Activando entorno virtual..."
source .venv/bin/activate || .venv/Scripts/activate

# Instalar dependencias
print_step "Instalando dependencias del backend..."
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    print_warning "Creando archivo .env desde env_example.txt..."
    cp env_example.txt .env
    print_warning "IMPORTANTE: Edita el archivo .env con tus configuraciones"
fi

# Inicializar base de datos
print_step "Inicializando base de datos..."
python init_db.py

print_success "Backend configurado correctamente"

# 2. Configurar frontend
print_step "Configurando frontend..."
cd ../frontend

# Instalar dependencias
print_step "Instalando dependencias del frontend..."
npm install

print_success "Frontend configurado correctamente"

# 3. Mostrar instrucciones
echo ""
echo "🎉 ¡Configuración completada!"
echo "============================="
echo ""
echo "Para iniciar el proyecto:"
echo ""
echo "📱 Backend:"
echo "   cd backend"
echo "   source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "🔗 URLs:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
print_warning "Recuerda configurar las variables en backend/.env"



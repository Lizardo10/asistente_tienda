@echo off
REM Script para iniciar Asistente Tienda completo en Windows
REM Incluye backend y frontend

echo 🏪 Asistente Tienda - Inicio Completo
echo =====================================

REM Verificar que estamos en el directorio correcto
if not exist "backend\app\main.py" (
    echo ❌ No se encontró backend\app\main.py. Ejecuta este script desde la raíz del proyecto.
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ No se encontró frontend\package.json. Ejecuta este script desde la raíz del proyecto.
    pause
    exit /b 1
)

REM Detener procesos existentes
echo ℹ️  Deteniendo procesos existentes...
taskkill //F //IM python.exe 2>nul || true
taskkill //F //IM node.exe 2>nul || true
taskkill //F //IM uvicorn.exe 2>nul || true
timeout /t 2 /nobreak >nul

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Verificar npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Configurar backend
echo ℹ️  Configurando backend...
cd backend

REM Verificar entorno virtual
if not exist "venv" (
    echo ⚠️  No se encontró el entorno virtual. Creando...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
if exist "requirements.txt" (
    echo ℹ️  Instalando dependencias del backend...
    pip install -r requirements.txt
)

REM Verificar archivo .env
if not exist ".env" (
    if exist "env_enhanced.txt" (
        echo ⚠️  No se encontró .env. Copiando desde env_enhanced.txt...
        copy env_enhanced.txt .env
        echo ⚠️  IMPORTANTE: Configura tu OPENAI_API_KEY en backend\.env
    ) else (
        echo ❌ No se encontró archivo .env ni env_enhanced.txt
        pause
        exit /b 1
    )
)

REM Volver al directorio raíz
cd ..

REM Configurar frontend
echo ℹ️  Configurando frontend...
cd frontend

REM Instalar dependencias
if not exist "node_modules" (
    echo ℹ️  Instalando dependencias del frontend...
    npm install
)

REM Volver al directorio raíz
cd ..

REM Mostrar información
echo.
echo 🏪 Asistente Tienda - Servicios Iniciados
echo ==========================================
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 💬 Chat Mejorado: http://localhost:5173/enhanced-chat
echo.
echo Presiona Ctrl+C para detener todos los servicios
echo.

REM Iniciar backend en una nueva ventana
echo 🚀 Iniciando backend de Asistente Tienda...
start "Asistente Tienda Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && echo 🚀 Backend iniciando en http://localhost:8000 && echo 📚 API Docs en http://localhost:8000/docs && echo 🏪 Asistente Tienda Backend && echo. && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Esperar un poco para que el backend inicie
timeout /t 5 /nobreak >nul

REM Iniciar frontend en una nueva ventana
echo 🎨 Iniciando frontend de Asistente Tienda...
start "Asistente Tienda Frontend" cmd /k "cd frontend && echo 🎨 Frontend iniciando en http://localhost:5173 && echo 🏪 Asistente Tienda Frontend && echo. && npm run dev"

echo ✅ Servicios iniciados en ventanas separadas
echo.
echo Para detener los servicios, cierra las ventanas de comandos o presiona Ctrl+C en cada una
pause

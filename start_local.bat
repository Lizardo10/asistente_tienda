@echo off
REM Script para iniciar el proyecto en modo desarrollo local (Windows)

echo 🚀 Iniciando proyecto en modo desarrollo local...
echo ================================================

REM Verificar que estamos en el directorio correcto
if not exist "backend" (
    echo ❌ Error: Ejecuta este script desde el directorio raíz del proyecto
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: Ejecuta este script desde el directorio raíz del proyecto
    pause
    exit /b 1
)

REM 1. Configurar backend
echo [PASO] Configurando backend...
cd backend

REM Crear entorno virtual si no existe
if not exist ".venv" (
    echo [PASO] Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
echo [PASO] Activando entorno virtual...
call .venv\Scripts\activate

REM Instalar dependencias
echo [PASO] Instalando dependencias del backend...
pip install -r requirements.txt

REM Crear archivo .env si no existe
if not exist ".env" (
    echo ⚠️  Creando archivo .env desde env_example.txt...
    copy env_example.txt .env
    echo ⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones
)

REM Inicializar base de datos
echo [PASO] Inicializando base de datos...
python init_db.py

echo ✅ Backend configurado correctamente

REM 2. Configurar frontend
echo [PASO] Configurando frontend...
cd ..\frontend

REM Instalar dependencias
echo [PASO] Instalando dependencias del frontend...
npm install

echo ✅ Frontend configurado correctamente

REM 3. Mostrar instrucciones
echo.
echo 🎉 ¡Configuración completada!
echo =============================
echo.
echo Para iniciar el proyecto:
echo.
echo 📱 Backend:
echo    cd backend
echo    .venv\Scripts\activate
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 🌐 Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 🔗 URLs:
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo.
echo ⚠️  Recuerda configurar las variables en backend\.env
echo.
pause



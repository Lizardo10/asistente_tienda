@echo off
echo ========================================
echo   INICIANDO PROYECTO TIENDA ASISTENTE
echo ========================================
echo.

echo 1. Configurando archivo .env...
if not exist "backend\.env" (
    copy "backend\env_example.txt" "backend\.env"
    echo ✅ Archivo .env creado
) else (
    echo ⚠️  El archivo .env ya existe
)
echo.

echo 2. Verificando PostgreSQL...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PostgreSQL no está instalado o no está en el PATH
    echo Por favor instala PostgreSQL desde: https://www.postgresql.org/download/windows/
    echo Y asegúrate de agregarlo al PATH del sistema
    pause
    exit /b 1
) else (
    echo ✅ PostgreSQL encontrado
)
echo.

echo 3. Creando base de datos PostgreSQL...
echo Creando base de datos 'tienda_asistente'...
psql -U postgres -c "CREATE DATABASE tienda_asistente;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Base de datos 'tienda_asistente' creada
) else (
    echo ⚠️  La base de datos ya existe o hubo un error
)
echo.

echo 4. Instalando dependencias del backend...
cd backend
pip install -r requirements.txt
echo ✅ Dependencias del backend instaladas
echo.

echo 5. Inicializando base de datos con datos de ejemplo...
python init_db.py
echo ✅ Base de datos inicializada con datos de ejemplo
echo.

echo 6. Iniciando backend...
start "Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✅ Backend iniciado en http://localhost:8000
echo.

echo 7. Instalando dependencias del frontend...
cd ..\frontend
npm install
echo ✅ Dependencias del frontend instaladas
echo.

echo 8. Iniciando frontend...
start "Frontend" cmd /k "npm run dev"
echo ✅ Frontend iniciado en http://localhost:5173
echo.

echo ========================================
echo   ¡PROYECTO INICIADO CORRECTAMENTE!
echo ========================================
echo.
echo 📋 Credenciales de acceso:
echo    Admin: admin@tienda.com / admin123
echo    Cliente: cliente@ejemplo.com / cliente123
echo.
echo 🌐 URLs:
echo    Frontend: http://localhost:5173
echo    Backend: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Presiona cualquier tecla para salir...
pause >nul

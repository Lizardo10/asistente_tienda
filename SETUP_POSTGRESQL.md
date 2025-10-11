# 🐘 Configuración de PostgreSQL

## Instalación de PostgreSQL

### 1. Descargar PostgreSQL
- Ve a: https://www.postgresql.org/download/windows/
- Descarga la versión más reciente para Windows
- Ejecuta el instalador

### 2. Configuración durante la instalación
- **Puerto**: Deja el puerto por defecto (5432)
- **Contraseña del usuario postgres**: Crea una contraseña segura (ejemplo: `postgres`)
- **Configuración regional**: Deja los valores por defecto

### 3. Verificar instalación
Abre una nueva terminal/cmd y ejecuta:
```bash
psql --version
```

## Configuración de la Base de Datos

### 1. Conectar a PostgreSQL
```bash
psql -U postgres
```

### 2. Crear la base de datos
```sql
CREATE DATABASE tienda_asistente;
```

### 3. Verificar que se creó
```sql
\l
```

### 4. Salir de psql
```sql
\q
```

## Configuración del Proyecto

### 1. Variables de entorno
El archivo `.env` ya está configurado con:
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tienda_asistente
```

### 2. Cambiar contraseña si es necesario
Si tu contraseña de PostgreSQL no es `postgres`, edita el archivo `backend/.env`:
```
DATABASE_URL=postgresql+psycopg2://postgres:TU_CONTRASEÑA@localhost:5432/tienda_asistente
```

## Iniciar el Proyecto

### Opción 1: Script automático
```bash
start_project.bat
```

### Opción 2: Manual
```bash
# 1. Configurar .env
copy backend\env_example.txt backend\.env

# 2. Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# 3. Crear base de datos
python init_db.py

# 4. Iniciar backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. En otra terminal, instalar dependencias del frontend
cd frontend
npm install

# 6. Iniciar frontend
npm run dev
```

## URLs del Proyecto

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Credenciales de Acceso

- **Admin**: admin@tienda.com / admin123
- **Cliente**: cliente@ejemplo.com / cliente123

## Solución de Problemas

### Error: "psql no se reconoce como comando"
- PostgreSQL no está en el PATH del sistema
- Agrega `C:\Program Files\PostgreSQL\[versión]\bin` al PATH del sistema
- O reinstala PostgreSQL y marca la opción "Add to PATH"

### Error: "authentication failed"
- Verifica que la contraseña en el `.env` sea correcta
- Prueba conectarte manualmente: `psql -U postgres -h localhost`

### Error: "database does not exist"
- Ejecuta: `psql -U postgres -c "CREATE DATABASE tienda_asistente;"`

### Error: "connection refused"
- Verifica que el servicio de PostgreSQL esté ejecutándose
- En Windows: Servicios > PostgreSQL > Iniciar

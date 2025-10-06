# Proyecto Integrador — Asistente Inteligente para Soporte Técnico de una Tienda Online

Este es un **esqueleto funcional** listo para crecer por módulos:
- **Backend (FastAPI + SQLAlchemy + JWT + WebSocket)** en `backend/`
- **Frontend (Vue 3 + Vite)** en `frontend/`
- **Ingesta RAG (LangChain + FAISS)** en `backend/scripts/ingest_docs.py`
- **PostgreSQL** (conectarse vía variables de entorno).

> Basado en el requerimiento del documento del proyecto (Frontend, API REST, BD, WebSocket, Chatbot, RAG, Panel Admin).

---

## Requisitos

- **Python 3.11+**
- **Node 18+ / PNPM o NPM** (usaremos NPM en los pasos)
- **PostgreSQL 14+** (y opcionalmente PgAdmin)
- **(Opcional) OpenAI API key** para el chatbot y RAG

---

## Pasos rápidos de ejecución (desarrollo)

### 1) Backend
```bash
cd backend
# Crear y activar entorno virtual (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac:
# python3 -m venv .venv
# source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env   # (Windows)  |  cp .env.example .env  (Linux/Mac)
# Edita .env con tus credenciales de PostgreSQL, JWT_SECRET y OPENAI_API_KEY (si lo usarás)

# Inicializar base de datos (crea tablas)
python init_db.py

# Ejecutar servidor
uvicorn app.main:app --reload --port 8000
```
El backend expone:
- `GET /health`
- `POST /auth/register`, `POST /auth/login`
- `GET /products`, `POST /products` (requiere token admin si lo aplicas)
- `GET /orders`, `POST /orders`
- WebSocket en `ws://localhost:8000/ws/support`

### 2) Frontend
```bash
cd frontend
npm install
# Copiar env de ejemplo
copy .env.example .env   # (Windows)  |  cp .env.example .env  (Linux/Mac)
# En .env define VITE_API_BASE=http://localhost:8000

npm run dev
```
Abre el navegador en la URL que indique Vite (típicamente `http://localhost:5173`).

### 3) RAG — Ingesta de documentos
Coloca tus PDFs/TXT/MD en `docs/` (carpeta del proyecto raíz o backend/docs). Por defecto usamos `backend/docs`.
Luego ejecuta:
```bash
cd backend
python scripts/ingest_docs.py
```
Esto genera un índice FAISS en `backend/rag_index/`. El endpoint de chat consumirá el índice si existe.

---

## Estructura de carpetas

```
tienda-asistente/
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ db.py
│  │  ├─ auth.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ utils.py
│  │  ├─ services/
│  │  │  ├─ openai_service.py
│  │  │  └─ rag_service.py
│  │  └─ routers/
│  │     ├─ auth.py
│  │     ├─ products.py
│  │     ├─ orders.py
│  │     └─ chat.py
│  ├─ scripts/
│  │  └─ ingest_docs.py
│  ├─ docs/           # coloca aquí PDFs/TXT/MD
│  ├─ requirements.txt
│  ├─ .env.example
│  └─ init_db.py
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js
│  ├─ .env.example
│  └─ src/
│     ├─ main.js
│     ├─ App.vue
│     ├─ router/index.js
│     ├─ views/{Home.vue, Admin.vue, Support.vue}
│     ├─ components/{Login.vue, ProductList.vue, Cart.vue, ChatWidget.vue}
│     └─ services/api.js
├─ docs/              # opcional, para documentación del proyecto
└─ .gitignore
```

---

## Notas

- Esto es un **punto de partida**: los controladores/routers tienen lógica mínima para que puedas entender y extender.
- El **WebSocket** graba mensajes en la BD y, si existe `OPENAI_API_KEY`, intentará responder usando el servicio de OpenAI y el índice RAG si lo generas.
- Si no tienes key de OpenAI, el bot responderá con un **mensaje simulado** para que puedas probar el flujo.
- Autenticación con **JWT** simple. Mejora el manejo de roles y permisos según tus necesidades.
- Para producción, agrega **Alembic** (migraciones), **Docker Compose**, pruebas automatizadas, mejores validaciones y manejo de errores.

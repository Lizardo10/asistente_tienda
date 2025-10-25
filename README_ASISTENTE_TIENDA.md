# 🏪 Asistente Tienda - Chat Inteligente

Sistema de chat inteligente con integración completa de OpenAI, procesamiento de audio e imágenes para una tienda online moderna.

## ✨ Características Principales

- **🤖 IA Avanzada**: Integración completa con OpenAI GPT-4
- **🎤 Reconocimiento de Voz**: Transcripción de audio usando Whisper AI
- **📸 Análisis de Imágenes**: Procesamiento de imágenes con Hugging Face
- **🛍️ Recomendaciones Inteligentes**: Sugerencias de productos basadas en IA
- **💬 Chat en Tiempo Real**: WebSocket para comunicación instantánea
- **🎨 UI Moderna**: Interfaz elegante con Tailwind CSS
- **🔐 Autenticación Completa**: Sistema de usuarios con roles y MFA
- **📊 Panel de Administración**: Dashboard completo para gestión

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

**Para Linux/Mac:**
```bash
./start_asistente_tienda.sh
```

**Para Windows:**
```cmd
start_asistente_tienda.bat
```

### Opción 2: Inicio Manual

**1. Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env_enhanced.txt .env
# Configura tu OPENAI_API_KEY en .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Chat Mejorado**: http://localhost:5173/enhanced-chat
- **Panel Admin**: http://localhost:5173/admin

## ⚙️ Configuración

### Variables de Entorno Importantes

Copia `backend/env_enhanced.txt` a `backend/.env` y configura:

```env
# REQUERIDO para chat inteligente
OPENAI_API_KEY=tu_openai_api_key_aqui

# OPCIONAL para análisis de imágenes
HUGGINGFACE_API_KEY=tu_huggingface_api_key_aqui

# OPCIONAL para caché
REDIS_URL=redis://localhost:6379

# OPCIONAL para pagos
PAYPAL_CLIENT_ID=tu_paypal_client_id_aqui
PAYPAL_CLIENT_SECRET=tu_paypal_client_secret_aqui
```

### Obtener API Keys

1. **OpenAI API Key**: https://platform.openai.com/api-keys
2. **Hugging Face API Key**: https://huggingface.co/settings/tokens
3. **PayPal Developer**: https://developer.paypal.com/

## 🏗️ Arquitectura

```
Asistente Tienda/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── core/           # Configuración centralizada
│   │   ├── models/         # Modelos de datos
│   │   ├── routers/        # Endpoints de la API
│   │   ├── services/       # Servicios de negocio
│   │   └── use_cases/      # Casos de uso (Clean Architecture)
│   ├── requirements.txt    # Dependencias Python
│   └── env_enhanced.txt   # Variables de entorno ejemplo
├── frontend/               # Aplicación Vue.js
│   ├── src/
│   │   ├── components/     # Componentes Vue
│   │   ├── views/          # Páginas
│   │   ├── services/       # Servicios API
│   │   └── router/         # Enrutamiento
│   └── package.json        # Dependencias Node.js
└── scripts/                # Scripts de inicio
```

## 🔧 Tecnologías Utilizadas

### Backend
- **FastAPI 0.115.0**: Framework web moderno
- **SQLModel**: ORM con validación automática
- **PostgreSQL**: Base de datos principal
- **Redis**: Sistema de caché
- **OpenAI**: Integración con GPT-4 y Whisper
- **Hugging Face**: Análisis de imágenes
- **WebSocket**: Comunicación en tiempo real

### Frontend
- **Vue.js 3**: Framework progresivo
- **Vite**: Herramienta de construcción rápida
- **Tailwind CSS**: Framework de estilos
- **Vue Router**: Enrutamiento SPA
- **Axios**: Cliente HTTP

## 📱 Funcionalidades del Chat

### 💬 Chat de Texto
- Respuestas inteligentes con OpenAI GPT-4
- Recomendaciones de productos automáticas
- Análisis de intención del usuario
- Historial de conversaciones

### 🎤 Chat de Audio
- Transcripción automática con Whisper AI
- Procesamiento de audio en tiempo real
- Soporte para múltiples formatos de audio

### 📸 Chat con Imágenes
- Análisis de imágenes con Hugging Face
- Reconocimiento de productos en fotos
- Recomendaciones basadas en imágenes

## 👥 Sistema de Usuarios

### Roles Disponibles
- **Cliente**: Acceso a productos y chat
- **Admin**: Panel de administración completo

### Funcionalidades de Admin
- Gestión de productos
- Gestión de pedidos
- Analytics del chat
- Gestión de usuarios
- Contabilidad básica

## 🛠️ Desarrollo

### Estructura de Clean Architecture
```
app/
├── domain/          # Entidades y reglas de negocio
├── application/     # Casos de uso
├── infrastructure/  # Implementaciones concretas
└── presentation/    # Controladores y rutas
```

### Principios SOLID
- **S**: Single Responsibility
- **O**: Open/Closed
- **L**: Liskov Substitution
- **I**: Interface Segregation
- **D**: Dependency Inversion

## 🧪 Testing

### Probar Chat Mejorado
```bash
python test_enhanced_chat.py
```

### Probar API
```bash
curl http://localhost:8000/health
```

## 📚 Documentación Adicional

- [Chat Mejorado](CHAT_ENHANCED_README.md): Documentación completa del chat
- [Configuración AWS](docs/informacion_tienda.md): Información de despliegue

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas:

1. Verifica que todas las dependencias estén instaladas
2. Confirma que las variables de entorno estén configuradas
3. Revisa los logs del backend y frontend
4. Consulta la documentación de la API en `/docs`

---

**🏪 Asistente Tienda** - Tu tienda inteligente con IA

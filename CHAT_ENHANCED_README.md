# 🏪 Asistente Tienda - Chat Inteligente

## ✨ Características de Asistente Tienda

- **🤖 IA Avanzada**: Integración completa con OpenAI GPT-4
- **🎤 Reconocimiento de Voz**: Transcripción de audio usando Whisper AI
- **📸 Análisis de Imágenes**: Procesamiento de imágenes con Hugging Face
- **🛍️ Recomendaciones Inteligentes**: Sugerencias de productos basadas en IA
- **💬 Chat en Tiempo Real**: WebSocket para comunicación instantánea
- **🎨 UI Moderna**: Interfaz elegante con Tailwind CSS

## 🛠️ Instalación y Configuración

### 1. Configurar Variables de Entorno

Copia el archivo de configuración:
```bash
cp backend/env_enhanced.txt backend/.env
```

Edita `backend/.env` y configura tu API key de OpenAI:
```env
OPENAI_API_KEY=tu_openai_api_key_aqui
```

### 2. Instalar Dependencias

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3. Inicializar Base de Datos

```bash
cd backend
python init_db.py
```

### 4. Iniciar Servidores

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🎯 Uso del Chat Mejorado

### Acceder al Chat
Visita: http://localhost:5173/enhanced-chat

### Funcionalidades Disponibles

#### 💬 Mensajes de Texto
- Escribe mensajes normalmente
- El asistente responde con IA avanzada
- Recibe recomendaciones de productos

#### 🎤 Mensajes de Audio
- Sube archivos de audio (WAV, MP3, M4A, WebM, OGG)
- El sistema transcribe automáticamente
- Procesa la transcripción como mensaje de texto

#### 📸 Mensajes con Imágenes
- Sube imágenes (JPG, PNG, GIF, WebP)
- El sistema analiza la imagen
- Busca productos similares automáticamente
- Proporciona recomendaciones basadas en la imagen

## 🔧 Endpoints de la API

### Chat Mejorado
- `POST /api/chat-enhanced/message` - Enviar mensaje de texto
- `POST /api/chat-enhanced/audio` - Enviar mensaje de audio
- `POST /api/chat-enhanced/image` - Enviar mensaje con imagen
- `POST /api/chat-enhanced/upload-audio` - Subir archivo de audio
- `POST /api/chat-enhanced/upload-image` - Subir archivo de imagen
- `GET /api/chat-enhanced/health` - Estado de los servicios
- `WebSocket /api/chat-enhanced/ws/enhanced` - Chat en tiempo real

### Servicios Individuales
- `POST /api/audio/transcribe` - Transcribir audio
- `POST /api/image-search/search` - Buscar productos por imagen

## 🧪 Pruebas

Ejecuta el script de pruebas para verificar que todo funcione:

```bash
python test_enhanced_chat.py
```

## 📋 Configuración Avanzada

### OpenAI API Key
1. Ve a https://platform.openai.com/api-keys
2. Crea una nueva API key
3. Configúrala en `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-tu-api-key-aqui
   ```

### Hugging Face API Key (Opcional)
1. Ve a https://huggingface.co/settings/tokens
2. Crea un token de acceso
3. Configúralo en `backend/.env`:
   ```env
   HUGGINGFACE_API_KEY=hf_tu-token-aqui
   ```

## 🎨 Personalización

### Modificar el Prompt del Asistente
Edita `backend/app/routers/chat_enhanced.py` línea 182 para personalizar la personalidad del asistente.

### Agregar Nuevos Tipos de Mensaje
Extiende el sistema agregando nuevos tipos en el router y el componente Vue.

### Personalizar Recomendaciones
Modifica las funciones `get_product_recommendations` y `search_products_by_image_description`.

## 🚨 Solución de Problemas

### Error: "OpenAI client not initialized"
- Verifica que tu `OPENAI_API_KEY` esté configurada correctamente
- Asegúrate de que la API key sea válida y tenga créditos

### Error: "Servicio de transcripción no disponible"
- Verifica la configuración de OpenAI
- Asegúrate de que el archivo de audio sea válido

### Error: "Error analizando la imagen"
- Verifica la configuración de Hugging Face
- Asegúrate de que el archivo de imagen sea válido

### El chat no responde
- Verifica que el backend esté ejecutándose en el puerto 8000
- Revisa los logs del backend para errores
- Asegúrate de que la base de datos esté inicializada

## 📊 Monitoreo

### Verificar Estado de Servicios
```bash
curl http://localhost:8000/api/chat-enhanced/health
```

### Logs del Backend
Los logs aparecen en la consola donde ejecutaste `uvicorn`.

## 🔄 Actualizaciones

Para actualizar el sistema:
1. Detén los servidores
2. Actualiza el código
3. Reinicia los servidores
4. Ejecuta las pruebas

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del backend
2. Ejecuta el script de pruebas
3. Verifica la configuración de las API keys
4. Asegúrate de que todas las dependencias estén instaladas

## 🎉 ¡Disfruta del Chat Inteligente!

Tu asistente ahora puede:
- Responder preguntas inteligentemente
- Procesar audio y convertirlo a texto
- Analizar imágenes y buscar productos similares
- Proporcionar recomendaciones personalizadas
- Mantener conversaciones contextuales

¡El futuro del comercio electrónico está aquí! 🚀



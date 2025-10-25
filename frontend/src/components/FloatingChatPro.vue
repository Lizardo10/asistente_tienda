<template>
  <div class="floating-chat-container">
    <!-- Botón flotante -->
    <button 
      v-if="!isOpen"
      @click="toggleChat"
      class="chat-fab"
      aria-label="Abrir chat de soporte"
    >
      <div class="fab-icon">
        <i class="fas fa-comments"></i>
      </div>
      <div class="fab-pulse"></div>
      <span v-if="unreadMessages > 0" class="notification-badge">{{ unreadMessages }}</span>
    </button>

    <!-- Ventana del chat -->
    <Transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">
        <!-- Header -->
        <div class="chat-header">
          <div class="header-left">
            <div class="bot-avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="bot-info">
              <h4 class="bot-name">Asistente IA</h4>
              <p class="bot-status">
                <span v-if="isTyping" class="typing">
                  <i class="fas fa-circle-notch fa-spin mr-1"></i>
                  Escribiendo...
                </span>
                <span v-else class="online">
                  <i class="fas fa-circle mr-1"></i>
                  En línea
                </span>
              </p>
            </div>
          </div>
          <div class="header-right">
            <button @click="minimizeChat" class="header-btn" title="Minimizar">
              <i class="fas fa-minus"></i>
            </button>
            <button @click="toggleChat" class="header-btn" title="Cerrar">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <!-- Mensajes -->
        <div ref="messagesContainer" class="messages-container">
          <!-- Pantalla de bienvenida -->
          <div v-if="!messages || messages.length === 0" class="welcome-screen">
            <div class="welcome-icon">
              <i class="fas fa-robot"></i>
            </div>
            <h3 class="welcome-title">¡Hola! 👋</h3>
            <p class="welcome-text">Soy tu asistente virtual. ¿En qué puedo ayudarte?</p>
            
            <div class="quick-actions">
              <button @click="sendQuickMessage('¿Qué productos tienen disponibles?')" class="quick-btn">
                <i class="fas fa-box-open mr-2"></i>
                Ver Productos
              </button>
              <button @click="sendQuickMessage('¿Cómo puedo hacer un pedido?')" class="quick-btn">
                <i class="fas fa-shopping-bag mr-2"></i>
                Hacer Pedido
              </button>
              <button @click="triggerImageUpload" class="quick-btn">
                <i class="fas fa-camera mr-2"></i>
                Buscar por Foto
              </button>
              <button @click="sendQuickMessage('¿Tienen envíos a domicilio?')" class="quick-btn">
                <i class="fas fa-truck mr-2"></i>
                Info de Envíos
              </button>
            </div>
          </div>

          <!-- Lista de mensajes -->
          <div 
            v-for="message in (messages || [])" 
            :key="message.id || Math.random()"
            class="message-wrapper"
            :class="{ 'user-message': message.type === 'user', 'bot-message': message.type === 'bot' }"
          >
            <div class="message-bubble">
              <div class="message-content">
                <p class="message-text">{{ message.text || message.content || 'Mensaje' }}</p>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              
              <!-- Productos recomendados -->
              <div v-if="message.products && message.products.length > 0" class="products-recommendations">
                <h5 class="products-title">Productos recomendados:</h5>
                <div class="products-grid">
                  <div 
                    v-for="product in message.products.slice(0, 3)" 
                    :key="product.id || Math.random()"
                    class="product-card"
                  >
                    <img :src="resolveImage(product.image_url)" :alt="product.title || 'Producto'" class="product-image">
                    <div class="product-info">
                      <h6 class="product-title">{{ product.title || 'Producto' }}</h6>
                      <p class="product-price">Q{{ (product.price || 0).toFixed(2) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input de audio -->
        <div v-if="audioPreview || isRecording" class="audio-section">
          <div v-if="audioPreview" class="audio-preview">
            <audio :src="audioPreview" controls class="audio-player"></audio>
            <div class="audio-actions">
              <button @click="sendAudioMessage" class="btn-send-audio" :disabled="isProcessingAudio">
                <i class="fas fa-paper-plane mr-1"></i>
                {{ isProcessingAudio ? 'Procesando...' : 'Enviar' }}
              </button>
              <button @click="clearAudio" class="btn-cancel-audio">
                <i class="fas fa-times mr-1"></i>
                Cancelar
              </button>
            </div>
          </div>
          
          <div v-if="isRecording" class="recording-indicator">
            <div class="recording-animation">
              <div class="pulse-ring"></div>
              <div class="pulse-ring"></div>
              <div class="pulse-ring"></div>
            </div>
            <span class="recording-text">Grabando... {{ recordingTime }}s</span>
          </div>
        </div>

        <!-- Input de mensaje -->
        <div class="input-section">
          <div class="input-controls">
            <button @click="triggerImageUpload" class="input-btn" title="Buscar por imagen">
              <i class="fas fa-camera"></i>
            </button>
            <button
              @mousedown="startRecording"
              @mouseup="stopRecording"
              @mouseleave="stopRecording"
              @touchstart="startRecording"
              @touchend="stopRecording"
              class="input-btn"
              :class="{ 'recording': isRecording }"
              title="Mantén presionado para grabar"
            >
              <i class="fas" :class="isRecording ? 'fa-stop' : 'fa-microphone'"></i>
            </button>
          </div>
          
          <div class="input-wrapper">
            <input
              v-model="newMessage"
              @keyup.enter="sendMessage"
              type="text"
              placeholder="Escribe tu mensaje..."
              class="message-input"
              :disabled="isSending"
            >
            <button 
              @click="sendMessage" 
              class="send-btn"
              :disabled="!newMessage.trim() || isSending"
            >
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Input oculto para imágenes -->
    <input
      ref="imageInput"
      type="file"
      accept="image/*"
      @change="handleImageUpload"
      style="display: none"
    >
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { session } from '../services/session'

// Estado reactivo
const isOpen = ref(false)
const isMinimized = ref(false)
const messages = ref([])
const newMessage = ref('')
const isSending = ref(false)
const isTyping = ref(false)
const unreadMessages = ref(0)
const chatId = ref(1)

// Audio
const audioPreview = ref(null)
const isRecording = ref(false)
const recordingTime = ref(0)
const recordingTimer = ref(null)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const isProcessingAudio = ref(false)

// Referencias
const messagesContainer = ref(null)
const imageInput = ref(null)

// Métodos principales
function toggleChat() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    unreadMessages.value = 0
    nextTick(() => scrollToBottom())
  }
}

function minimizeChat() {
  isMinimized.value = true
  isOpen.value = false
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  if (!newMessage.value.trim() || isSending.value) return

  const messageText = newMessage.value.trim()
  newMessage.value = ''
  
  // Agregar mensaje del usuario
  const userMessage = {
    id: Date.now(),
    type: 'user',
    text: messageText,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  
  // Guardar mensaje
  await saveMessage('user', messageText)
  
  nextTick(() => scrollToBottom())
  
  // Enviar al bot
  await sendToBot(messageText)
}

async function sendToBot(messageText) {
  try {
    isTyping.value = true
    
    const response = await api.post('/modern-chat/advanced-message', {
      chat_id: parseInt(chatId.value) || 1,
      message: messageText
    })
    
    isTyping.value = false
    
    const botResponse = response.data.response || 'Lo siento, no pude procesar tu mensaje.'
    
    const botMessage = {
      id: Date.now() + 1,
      type: 'bot',
      text: botResponse,
      timestamp: new Date(),
      products: response.data.recommendations || []
    }
    
    messages.value.push(botMessage)
    
    // Guardar respuesta del bot
    await saveMessage('bot', botResponse)
    
    nextTick(() => scrollToBottom())
    
  } catch (error) {
    console.error('Error enviando mensaje:', error)
    isTyping.value = false
    
    const errorMessage = {
      id: Date.now() + 1,
      type: 'bot',
      text: 'Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo.',
      timestamp: new Date()
    }
    
    messages.value.push(errorMessage)
    nextTick(() => scrollToBottom())
  }
}

function sendQuickMessage(message) {
  newMessage.value = message
  sendMessage()
}

// Audio
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    audioChunks.value = []
    
    // Detectar el mejor formato de audio disponible
    let mimeType = 'audio/webm'
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
      mimeType = 'audio/webm;codecs=opus'
    } else if (MediaRecorder.isTypeSupported('audio/webm')) {
      mimeType = 'audio/webm'
    } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
      mimeType = 'audio/mp4'
    } else if (MediaRecorder.isTypeSupported('audio/wav')) {
      mimeType = 'audio/wav'
    }
    
    console.log('🎤 Usando formato de audio:', mimeType)
    
    mediaRecorder.value = new MediaRecorder(stream, {
      mimeType: mimeType
    })
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    
    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(audioChunks.value || [], { type: mimeType })
      console.log('🎤 Audio grabado:', {
        type: audioBlob.type,
        size: audioBlob.size,
        chunks: (audioChunks.value || []).length,
        mimeType: mimeType
      })
      audioPreview.value = URL.createObjectURL(audioBlob)
      stream.getTracks().forEach(track => track.stop())
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0
    
    recordingTimer.value = setInterval(() => {
      recordingTime.value++
      if (recordingTime.value >= 30) {
        stopRecording()
      }
    }, 1000)
    
  } catch (error) {
    console.error('Error accediendo al micrófono:', error)
    alert('No se pudo acceder al micrófono. Por favor verifica los permisos.')
  }
}

function stopRecording() {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    
    if (recordingTimer.value) {
      clearInterval(recordingTimer.value)
      recordingTimer.value = null
    }
  }
}

async function sendAudioMessage() {
  if (!audioPreview.value) return
  
  try {
    isProcessingAudio.value = true
    
    // Convertir audio a texto
    const audioText = await convertAudioToText(audioPreview.value)
    
    if (audioText) {
      newMessage.value = audioText
      await sendMessage()
    } else {
      // Mostrar mensaje específico según el tipo de error
      let errorMessage = '🎤 Mensaje de audio enviado'
      if (error && error.message.includes('Audio muy corto')) {
        errorMessage = '🎤 Audio muy corto, intenta grabar por más tiempo'
      }
      
      const fallbackMessage = {
        id: Date.now(),
        type: 'user',
        text: errorMessage,
        timestamp: new Date()
      }
      messages.value.push(fallbackMessage)
      await sendToBot(errorMessage)
    }
    
    clearAudio()
    
  } catch (error) {
    console.error('Error procesando audio:', error)
  } finally {
    isProcessingAudio.value = false
  }
}

function clearAudio() {
  audioPreview.value = null
  if (audioPreview.value) {
    URL.revokeObjectURL(audioPreview.value)
  }
}

async function convertAudioToText(audioUrl) {
  try {
    const response = await fetch(audioUrl)
    const blob = await response.blob()
    
    // Determinar la extensión del archivo basada en el tipo MIME
    let filename = 'audio.webm'
    if (blob.type.includes('mp4')) {
      filename = 'audio.m4a'
    } else if (blob.type.includes('wav')) {
      filename = 'audio.wav'
    } else if (blob.type.includes('webm')) {
      filename = 'audio.webm'
    }
    
    console.log('🎤 Enviando audio:', filename, 'Tipo:', blob.type, 'Tamaño:', blob.size)
    
    // Validar que el audio tenga suficiente duración (al menos 0.5 segundos)
    if (blob.size < 1000) { // Menos de 1KB probablemente es muy corto
      console.log('🔧 Audio muy corto, tamaño:', blob.size)
      throw new Error('Audio muy corto, intenta grabar por más tiempo (al menos 1 segundo)')
    }
    
    const base64 = await new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result.split(',')[1]
        resolve(result)
      }
      reader.readAsDataURL(blob)
    })
    
    const transcriptionResponse = await api.post('/audio/transcribe-base64', {
      audio_data: base64,
      filename: filename,
      language: 'es'
    })
    
    if (transcriptionResponse.data.success && transcriptionResponse.data.transcript) {
      console.log('✅ Transcripción exitosa:', transcriptionResponse.data.transcript)
      return transcriptionResponse.data.transcript
    }
    
    console.warn('⚠️ Transcripción falló o vacía')
    return null
    
  } catch (error) {
    console.error('❌ Error en transcripción:', error)
    if (error.response?.status === 503) {
      console.error('🔧 Servicio de transcripción no disponible')
    } else if (error.response?.status === 400) {
      console.error('🔧 Formato de audio no soportado o muy corto')
    } else if (error.message.includes('Audio muy corto')) {
      console.error('🔧 Audio muy corto:', error.message)
    }
    return null
  }
}

// Imágenes
function triggerImageUpload() {
  imageInput.value.click()
}

async function handleImageUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/image-search/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    if (response.data.success) {
      const analysis = response.data.image_analysis
      const similarProducts = response.data.similar_products
      
      let messageText = `Analicé esta imagen: ${file.name}\n`
      messageText += `Descripción: ${analysis.description}\n`
      
      if (similarProducts && similarProducts.length > 0) {
        messageText += `Encontré ${similarProducts.length} productos similares:\n`
        similarProducts.slice(0, 3).forEach((product, index) => {
          messageText += `${index + 1}. ${product.title} - Q${product.price}\n`
        })
      } else {
        messageText += `No encontré productos similares específicos, pero puedo ayudarte a buscar productos relacionados.`
      }
      
      newMessage.value = messageText
    } else {
      newMessage.value = `Subí una imagen: ${file.name}. ¿Puedes ayudarme a encontrar productos similares?`
    }
    
    await sendMessage()
    
  } catch (error) {
    console.error('Error procesando imagen:', error)
    alert('Error procesando la imagen. Por favor intenta de nuevo.')
  }
}

// Utilidades
function formatTime(timestamp) {
  if (!timestamp) return new Date().toLocaleTimeString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
  return new Date(timestamp).toLocaleTimeString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

function resolveImage(imageUrl) {
  if (!imageUrl) return 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&h=100&fit=crop'
  if (imageUrl.startsWith('http')) return imageUrl
  return `http://localhost:8000${imageUrl}`
}

async function saveMessage(sender, content) {
  try {
    const userEmail = session.user?.email || 'Usuario Guest'
    const userId = session.user?.id || null
    
    if (!chatId.value) {
      chatId.value = 1
    }
    
    const messagePayload = {
      chat_id: chatId.value,
      user_id: userId,
      user_email: userEmail,
      content: content,
      sender: sender,
      message_type: 'text',
      message_data: JSON.stringify({})
    }
    
    await api.post('/chat-history/save-message', messagePayload)
    
  } catch (error) {
    console.error('Error guardando mensaje:', error)
  }
}

// Inicialización
onMounted(() => {
  // Generar chat_id único
  chatId.value = 1
})
</script>

<style scoped>
.floating-chat-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

/* Botón flotante */
.chat-fab {
  position: relative;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.chat-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
}

.fab-pulse {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  animation: pulse 2s infinite;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* Ventana del chat */
.chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.chat-header {
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  color: white;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.bot-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
}

.bot-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.bot-status {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

.header-right {
  display: flex;
  gap: 8px;
}

.header-btn {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Mensajes */
.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f8fafc;
}

.welcome-screen {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 32px;
  color: white;
}

.welcome-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.welcome-text {
  color: #6b7280;
  margin-bottom: 30px;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-btn {
  padding: 12px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #f3f4f6;
  border-color: #ff8c00;
}

.message-wrapper {
  margin-bottom: 16px;
}

.user-message {
  display: flex;
  justify-content: flex-end;
}

.bot-message {
  display: flex;
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.bot-message .message-bubble {
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}

.message-text {
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
}

/* Productos recomendados */
.products-recommendations {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.products-title {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.product-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 8px;
  text-align: center;
}

.product-image {
  width: 100%;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 4px;
}

.product-title {
  font-size: 10px;
  font-weight: 500;
  margin: 0 0 2px 0;
  color: #374151;
}

.product-price {
  font-size: 9px;
  color: #ff8c00;
  font-weight: 600;
  margin: 0;
}

/* Audio */
.audio-section {
  padding: 16px 20px;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.audio-preview {
  display: flex;
  align-items: center;
  gap: 12px;
}

.audio-player {
  flex: 1;
  height: 40px;
}

.audio-actions {
  display: flex;
  gap: 8px;
}

.btn-send-audio {
  padding: 8px 16px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
}

.btn-cancel-audio {
  padding: 8px 16px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
}

.recording-animation {
  position: relative;
  width: 20px;
  height: 20px;
}

.pulse-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid #ef4444;
  border-radius: 50%;
  animation: pulse-ring 1.5s infinite;
}

.pulse-ring:nth-child(2) {
  animation-delay: 0.5s;
}

.pulse-ring:nth-child(3) {
  animation-delay: 1s;
}

.recording-text {
  color: #dc2626;
  font-size: 14px;
  font-weight: 500;
}

/* Input */
.input-section {
  padding: 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.input-btn {
  width: 36px;
  height: 36px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.input-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.input-btn.recording {
  background: #ef4444;
  color: white;
  animation: pulse 1s infinite;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #ff8c00;
}

.send-btn {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animaciones */
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

/* Responsive */
@media (max-width: 480px) {
  .chat-window {
    width: calc(100vw - 40px);
    height: calc(100vh - 100px);
    bottom: 80px;
    right: 20px;
  }
}
</style>
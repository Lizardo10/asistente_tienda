<template>
  <div>
    <!-- Botón flotante para abrir el chat -->
    <button 
      v-if="!isOpen"
      @click="toggleChat"
      class="chat-fab"
      aria-label="Abrir chat de soporte"
    >
      <i class="fas fa-comments fa-lg"></i>
      <span v-if="unreadMessages > 0" class="badge-notification">{{ unreadMessages }}</span>
    </button>

    <!-- Ventana del chat -->
    <Transition name="chat-slide">
      <div v-if="isOpen" class="chat-container">
        <!-- Header del chat -->
        <div class="chat-header">
          <div class="d-flex align-items-center">
            <div class="chat-avatar me-2">
              <i class="fas fa-robot"></i>
            </div>
            <div>
              <h6 class="mb-0">Asistente Virtual</h6>
              <small class="text-white-50">
                <span v-if="!isTyping" class="status-dot"></span>
                {{ isTyping ? 'Escribiendo...' : 'En línea' }}
              </small>
            </div>
          </div>
          <div class="chat-actions">
            <button @click="minimizeChat" class="btn-icon" title="Minimizar">
              <i class="fas fa-minus"></i>
            </button>
            <button @click="toggleChat" class="btn-icon" title="Cerrar">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <!-- Mensajes del chat -->
        <div ref="messagesContainer" class="chat-messages">
          <!-- Mensaje de bienvenida -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">
              <i class="fas fa-robot fa-3x"></i>
            </div>
            <h5>¡Hola! 👋</h5>
            <p>Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?</p>
            <div class="quick-actions mt-3">
              <button @click="sendQuickMessage('¿Qué productos tienen?')" class="quick-action-btn">
                <i class="fas fa-box me-2"></i>Ver productos
              </button>
              <button @click="sendQuickMessage('¿Cómo hago un pedido?')" class="quick-action-btn">
                <i class="fas fa-shopping-cart me-2"></i>Hacer pedido
              </button>
              <button @click="showImageUpload = true" class="quick-action-btn">
                <i class="fas fa-camera me-2"></i>Buscar por imagen
              </button>
            </div>
          </div>

          <!-- Mensajes -->
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            :class="['message', msg.type === 'user' ? 'message-user' : 'message-bot']"
          >
            <div class="message-avatar">
              <i :class="msg.type === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
            </div>
            <div class="message-content">
              <div class="message-bubble">
                <!-- Imagen si existe -->
                <img v-if="msg.image" :src="msg.image" class="message-image mb-2" alt="Imagen enviada">
                
                <!-- Texto del mensaje -->
                <div v-html="formatMessage(msg.text)"></div>
                
                <!-- Productos recomendados -->
                <div v-if="msg.products && msg.products.length > 0" class="recommended-products mt-3">
                  <strong class="d-block mb-2">Productos similares encontrados:</strong>
                  <div class="product-cards">
                    <div 
                      v-for="product in msg.products" 
                      :key="product.id"
                      class="product-card-mini"
                      @click="viewProduct(product.id)"
                    >
                      <img :src="product.image_url || '/placeholder.jpg'" :alt="product.title">
                      <div class="product-info">
                        <strong>{{ product.title }}</strong>
                        <span class="text-success">${{ product.price }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <small class="message-time">{{ formatTime(msg.timestamp) }}</small>
            </div>
          </div>

          <!-- Indicador de escritura -->
          <div v-if="isTyping" class="message message-bot">
            <div class="message-avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
              <div class="message-bubble typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input del chat -->
        <div class="chat-input">
          <!-- Vista previa de imagen -->
          <div v-if="imagePreview" class="image-preview mb-2">
            <img :src="imagePreview" alt="Preview">
            <button @click="clearImage" class="btn-remove-image">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <div class="input-group">
            <!-- Botón de imagen -->
            <button @click="triggerImageUpload" class="btn-icon" title="Buscar por imagen">
              <i class="fas fa-camera"></i>
            </button>
            <input 
              ref="imageInput"
              type="file"
              accept="image/*"
              @change="handleImageSelect"
              style="display: none"
            >

            <!-- Campo de texto -->
            <input 
              v-model="newMessage"
              @keyup.enter="sendMessage"
              @input="handleTyping"
              type="text"
              class="form-control chat-input-field"
              placeholder="Escribe tu mensaje..."
              :disabled="isSending"
            >

            <!-- Botón de enviar -->
            <button 
              @click="sendMessage"
              :disabled="isSending || (!newMessage.trim() && !selectedImage)"
              class="btn-send"
            >
              <i v-if="!isSending" class="fas fa-paper-plane"></i>
              <span v-else class="spinner-border spinner-border-sm"></span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

// Estado del chat
const isOpen = ref(false)
const messages = ref([])
const newMessage = ref('')
const isSending = ref(false)
const isTyping = ref(false)
const unreadMessages = ref(0)
const messagesContainer = ref(null)
const chatId = ref(null)
const userIsTyping = ref(false)
let typingTimeout = null

// Estado de imagen
const selectedImage = ref(null)
const imagePreview = ref(null)
const imageInput = ref(null)
const showImageUpload = ref(false)

// Métodos
const toggleChat = async () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    unreadMessages.value = 0
    
    // Crear chat si no existe
    if (!chatId.value) {
      await initializeChat()
    }
    
    nextTick(() => scrollToBottom())
  }
}

const minimizeChat = () => {
  isOpen.value = false
}

const initializeChat = async () => {
  try {
    // Crear sesión de chat
    const response = await api.post('/modern-chat/create')
    chatId.value = response.data.chat_id
    
    console.log('Chat inicializado:', chatId.value)
  } catch (error) {
    console.error('Error inicializando chat:', error)
    chatId.value = 1  // Fallback
  }
}

const handleTyping = () => {
  // Limpiar timeout anterior
  if (typingTimeout) {
    clearTimeout(typingTimeout)
  }
  
  // Marcar como escribiendo
  userIsTyping.value = true
  
  // Después de 1 segundo sin escribir, marcar como no escribiendo
  typingTimeout = setTimeout(() => {
    userIsTyping.value = false
  }, 1000)
}

const sendMessage = async () => {
  if (!newMessage.value.trim() && !selectedImage.value) return
  
  try {
    isSending.value = true
    
    // Si hay imagen, buscar por imagen
    if (selectedImage.value) {
      await searchByImage()
      return
    }
    
    // Agregar mensaje del usuario
    const userMessage = {
      type: 'user',
      text: newMessage.value,
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    const query = newMessage.value
    newMessage.value = ''
    
    // Scroll to bottom
    nextTick(() => scrollToBottom())
    
    // Mostrar indicador de escritura
    isTyping.value = true
    
    // Enviar mensaje al backend usando el endpoint correcto con RAG
    const response = await api.post('/modern-chat/advanced-message', {
      chat_id: chatId.value || 1,
      message: query
    })
    
    isTyping.value = false
    
    // Extraer respuesta y contexto
    const botResponse = response.data.response || response.data.content || 'Lo siento, no pude procesar tu mensaje.'
    const context = response.data.context || {}
    
    // Agregar respuesta del bot
    const botMessage = {
      type: 'bot',
      text: botResponse,
      timestamp: new Date(),
      products: context.products || [],
      intent: context.intent
    }
    messages.value.push(botMessage)
    
    nextTick(() => scrollToBottom())
    
    if (!isOpen.value) {
      unreadMessages.value++
    }
    
  } catch (error) {
    console.error('Error enviando mensaje:', error)
    isTyping.value = false
    
    const errorMessage = {
      type: 'bot',
      text: 'Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo.',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
    
  } finally {
    isSending.value = false
  }
}

const searchByImage = async () => {
  try {
    // Agregar mensaje del usuario con imagen
    const userMessage = {
      type: 'user',
      text: newMessage.value || 'Buscar productos similares a esta imagen',
      image: imagePreview.value,
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    newMessage.value = ''
    nextTick(() => scrollToBottom())
    
    // Mostrar indicador de escritura
    isTyping.value = true
    
    // Crear FormData con la imagen
    const formData = new FormData()
    formData.append('file', selectedImage.value)
    
    // Buscar productos por imagen
    const response = await api.post('/products/search/by-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    isTyping.value = false
    
    // Agregar respuesta con productos similares
    const botMessage = {
      type: 'bot',
      text: `He analizado la imagen y encontré ${response.data.total_found} productos similares:\n\n${response.data.image_analysis.description}\n\n${response.data.ai_recommendation}`,
      products: response.data.similar_products,
      timestamp: new Date()
    }
    messages.value.push(botMessage)
    
    // Limpiar imagen
    clearImage()
    nextTick(() => scrollToBottom())
    
  } catch (error) {
    console.error('Error buscando por imagen:', error)
    isTyping.value = false
    
    const errorMessage = {
      type: 'bot',
      text: 'Lo siento, hubo un error analizando la imagen. Por favor, intenta con otra imagen.',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
    
    clearImage()
  }
}

const sendQuickMessage = (message) => {
  newMessage.value = message
  sendMessage()
}

const triggerImageUpload = () => {
  imageInput.value?.click()
}

const handleImageSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    
    // Crear preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const clearImage = () => {
  selectedImage.value = null
  imagePreview.value = null
  if (imageInput.value) {
    imageInput.value.value = ''
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (text) => {
  // Convertir URLs en enlaces
  return text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>')
}

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('es-GT', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const viewProduct = (productId) => {
  router.push(`/product/${productId}`)
}

// Cargar mensajes guardados del localStorage
onMounted(() => {
  const savedMessages = localStorage.getItem('chatMessages')
  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages)
    } catch (e) {
      console.error('Error cargando mensajes:', e)
    }
  }
})

// Guardar mensajes en localStorage
watch(messages, (newMessages) => {
  localStorage.setItem('chatMessages', JSON.stringify(newMessages))
}, { deep: true })
</script>

<script>
import { watch } from 'vue'
export default {
  name: 'FloatingChat'
}
</script>

<style scoped>
/* Botón flotante */
.chat-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
  cursor: pointer;
  z-index: 999;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-fab:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 12px 40px rgba(99, 102, 241, 0.5);
}

.chat-fab:active {
  transform: scale(0.95);
}

.badge-notification {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: bold;
}

/* Contenedor del chat */
.chat-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.chat-header {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2ecc71;
  margin-right: 4px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Mensajes */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.welcome-icon {
  color: #6366f1;
  margin-bottom: 16px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action-btn {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  color: #333;
}

.quick-action-btn:hover {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-color: #6366f1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Mensaje individual */
.message {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.message-bot .message-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.message-user .message-avatar {
  background: #e0e0e0;
  color: #666;
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.message-user .message-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  word-wrap: break-word;
}

.message-bot .message-bubble {
  background: white;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message-user .message-bubble {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}

.message-time {
  color: #999;
  font-size: 11px;
  margin-top: 4px;
  padding: 0 4px;
}

.message-image {
  max-width: 200px;
  border-radius: 8px;
}

/* Indicador de escritura */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6366f1;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Productos recomendados */
.recommended-products {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}

.product-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-card-mini {
  display: flex;
  gap: 12px;
  background: white;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e0e0e0;
}

.product-card-mini:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-card-mini img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.product-info strong {
  font-size: 14px;
  color: #333;
}

.product-info span {
  font-size: 16px;
  font-weight: bold;
}

/* Input */
.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-input-field {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  padding: 12px 16px;
  font-size: 14px;
}

.chat-input-field:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-send {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-send:hover:not(:disabled) {
  transform: scale(1.15);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.5);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Preview de imagen */
.image-preview {
  position: relative;
  display: inline-block;
}

.image-preview img {
  max-width: 150px;
  border-radius: 8px;
}

.btn-remove-image {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ff4757;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 12px;
}

/* Animaciones */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

/* Responsive */
@media (max-width: 480px) {
  .chat-container {
    width: 100%;
    height: 100%;
    bottom: 0;
    right: 0;
    border-radius: 0;
  }
  
  .chat-fab {
    bottom: 16px;
    right: 16px;
  }
}

/* Scrollbar personalizado */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>


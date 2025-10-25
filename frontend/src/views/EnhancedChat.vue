<template>
  <div class="min-h-screen bg-gradient-hero">
    <!-- Header -->
    <div class="bg-white/10 backdrop-blur-lg border-b border-white/20">
      <div class="max-w-6xl mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-display font-bold text-white">
              🏪 Asistente Tienda
            </h1>
            <p class="text-white/80 mt-2">
              Chat inteligente con IA, audio e imágenes
            </p>
          </div>
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2 text-white/80">
              <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span class="text-sm">Conectado</span>
            </div>
            <button 
              @click="clearChat"
              class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all-smooth"
            >
              🗑️ Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Container -->
    <div class="max-w-6xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Chat Messages -->
        <div class="lg:col-span-2">
          <div class="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6 h-[600px] flex flex-col">
            
            <!-- Messages Area -->
            <div ref="messagesContainer" class="flex-1 overflow-y-auto space-y-4 mb-6">
              <div v-if="messages.length === 0" class="text-center text-white/60 py-8">
                <div class="text-6xl mb-4">👋</div>
                <p class="text-lg">¡Hola! Soy tu asistente inteligente</p>
                <p class="text-sm">Puedes escribir, enviar audio o imágenes</p>
              </div>
              
              <div v-for="message in messages" :key="message.id" class="flex" :class="message.sender === 'user' ? 'justify-end' : 'justify-start'">
                <div class="max-w-[80%] rounded-2xl p-4" :class="message.sender === 'user' ? 'bg-primary-500 text-white' : 'bg-white/20 text-white backdrop-blur-lg'">
                  
                  <!-- Message Type Indicator -->
                  <div v-if="message.message_type !== 'text'" class="text-xs opacity-70 mb-2">
                    <span v-if="message.message_type === 'audio'">🎤 Audio</span>
                    <span v-else-if="message.message_type === 'image'">📸 Imagen</span>
                  </div>
                  
                  <!-- Message Content -->
                  <div class="whitespace-pre-wrap">{{ message.content }}</div>
                  
                  <!-- Recommendations -->
                  <div v-if="message.recommendations && message.recommendations.length > 0" class="mt-4">
                    <div class="text-xs opacity-70 mb-2">✨ Recomendaciones:</div>
                    <div class="space-y-2">
                      <div v-for="rec in message.recommendations" :key="rec.id" class="bg-white/10 rounded-lg p-3">
                        <div class="font-semibold">{{ rec.title }}</div>
                        <div class="text-sm opacity-80">{{ rec.description }}</div>
                        <div class="text-sm font-bold text-green-300">${{ rec.price }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Image Analysis -->
                  <div v-if="message.image_analysis" class="mt-4">
                    <div class="text-xs opacity-70 mb-2">📸 Análisis:</div>
                    <div class="bg-white/10 rounded-lg p-3">
                      <div class="text-sm">{{ message.image_analysis.description }}</div>
                    </div>
                  </div>
                  
                  <!-- Timestamp -->
                  <div class="text-xs opacity-50 mt-2">
                    {{ formatTime(message.timestamp) }}
                  </div>
                </div>
              </div>
              
              <!-- Typing Indicator -->
              <div v-if="isTyping" class="flex justify-start">
                <div class="bg-white/20 backdrop-blur-lg rounded-2xl p-4 text-white">
                  <div class="flex items-center gap-2">
                    <div class="animate-pulse">🤖</div>
                    <span>Escribiendo...</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Input Area -->
            <div class="border-t border-white/20 pt-4">
              <!-- Message Type Selector -->
              <div class="flex items-center gap-2 mb-4">
                <button 
                  @click="messageType = 'text'"
                  :class="messageType === 'text' ? 'bg-primary-500 text-white' : 'bg-white/20 text-white'"
                  class="px-3 py-2 rounded-lg transition-all-smooth"
                >
                  💬 Texto
                </button>
                <button 
                  @click="messageType = 'audio'"
                  :class="messageType === 'audio' ? 'bg-primary-500 text-white' : 'bg-white/20 text-white'"
                  class="px-3 py-2 rounded-lg transition-all-smooth"
                >
                  🎤 Audio
                </button>
                <button 
                  @click="messageType = 'image'"
                  :class="messageType === 'image' ? 'bg-primary-500 text-white' : 'bg-white/20 text-white'"
                  class="px-3 py-2 rounded-lg transition-all-smooth"
                >
                  📸 Imagen
                </button>
              </div>
              
              <!-- Text Input -->
              <div v-if="messageType === 'text'" class="flex gap-2">
                <input
                  v-model="textMessage"
                  @keypress.enter="sendTextMessage"
                  placeholder="Escribe tu mensaje..."
                  class="flex-1 bg-white/20 backdrop-blur-lg border border-white/30 rounded-lg px-4 py-3 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-primary-400"
                  :disabled="isLoading"
                />
                <button
                  @click="sendTextMessage"
                  :disabled="!textMessage.trim() || isLoading"
                  class="px-6 py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-500 text-white rounded-lg transition-all-smooth btn-animate"
                >
                  <span v-if="!isLoading">📤</span>
                  <span v-else class="animate-spin">⏳</span>
                </button>
              </div>
              
              <!-- Audio Input -->
              <div v-if="messageType === 'audio'" class="space-y-4">
                <div class="flex gap-2">
                  <input
                    ref="audioInput"
                    type="file"
                    accept="audio/*"
                    @change="handleAudioFile"
                    class="hidden"
                  />
                  <button
                    @click="$refs.audioInput.click()"
                    class="flex-1 bg-white/20 backdrop-blur-lg border border-white/30 rounded-lg px-4 py-3 text-white hover:bg-white/30 transition-all-smooth"
                  >
                    📁 Seleccionar archivo de audio
                  </button>
                  <button
                    @click="startRecording"
                    :disabled="isRecording"
                    class="px-6 py-3 bg-red-500 hover:bg-red-600 disabled:bg-gray-500 text-white rounded-lg transition-all-smooth"
                  >
                    <span v-if="!isRecording">🎤</span>
                    <span v-else class="animate-pulse">⏹️</span>
                  </button>
                </div>
                
                <div v-if="selectedAudioFile" class="bg-white/10 rounded-lg p-3 text-white">
                  <div class="text-sm">📁 {{ selectedAudioFile.name }}</div>
                  <button
                    @click="sendAudioMessage"
                    :disabled="isLoading"
                    class="mt-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-all-smooth"
                  >
                    Enviar Audio
                  </button>
                </div>
              </div>
              
              <!-- Image Input -->
              <div v-if="messageType === 'image'" class="space-y-4">
                <div class="flex gap-2">
                  <input
                    ref="imageInput"
                    type="file"
                    accept="image/*"
                    @change="handleImageFile"
                    class="hidden"
                  />
                  <button
                    @click="$refs.imageInput.click()"
                    class="flex-1 bg-white/20 backdrop-blur-lg border border-white/30 rounded-lg px-4 py-3 text-white hover:bg-white/30 transition-all-smooth"
                  >
                    📁 Seleccionar imagen
                  </button>
                </div>
                
                <div v-if="selectedImageFile" class="bg-white/10 rounded-lg p-3 text-white">
                  <div class="text-sm mb-2">📸 {{ selectedImageFile.name }}</div>
                  <img :src="imagePreview" alt="Preview" class="w-32 h-32 object-cover rounded-lg mb-2" />
                  <button
                    @click="sendImageMessage"
                    :disabled="isLoading"
                    class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-all-smooth"
                  >
                    Analizar Imagen
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Sidebar -->
        <div class="space-y-6">
          
          <!-- Features Card -->
          <div class="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6">
            <h3 class="text-xl font-semibold text-white mb-4">✨ Funcionalidades</h3>
            <div class="space-y-3">
              <div class="flex items-center gap-3 text-white/80">
                <span class="text-2xl">🤖</span>
                <div>
                  <div class="font-semibold">IA Avanzada</div>
                  <div class="text-sm opacity-70">OpenAI GPT-4</div>
                </div>
              </div>
              <div class="flex items-center gap-3 text-white/80">
                <span class="text-2xl">🎤</span>
                <div>
                  <div class="font-semibold">Reconocimiento de Voz</div>
                  <div class="text-sm opacity-70">Whisper AI</div>
                </div>
              </div>
              <div class="flex items-center gap-3 text-white/80">
                <span class="text-2xl">📸</span>
                <div>
                  <div class="font-semibold">Análisis de Imágenes</div>
                  <div class="text-sm opacity-70">Hugging Face</div>
                </div>
              </div>
              <div class="flex items-center gap-3 text-white/80">
                <span class="text-2xl">🛍️</span>
                <div>
                  <div class="font-semibold">Recomendaciones</div>
                  <div class="text-sm opacity-70">Productos inteligentes</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Status Card -->
          <div class="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6">
            <h3 class="text-xl font-semibold text-white mb-4">📊 Estado</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between text-white/80">
                <span>OpenAI</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span class="text-sm">Activo</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-white/80">
                <span>Audio</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span class="text-sm">Activo</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-white/80">
                <span>Imágenes</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span class="text-sm">Activo</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Quick Actions -->
          <div class="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6">
            <h3 class="text-xl font-semibold text-white mb-4">⚡ Acciones Rápidas</h3>
            <div class="space-y-2">
              <button
                @click="sendQuickMessage('¿Qué productos tienen disponibles?')"
                class="w-full text-left px-3 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all-smooth"
              >
                📦 Ver productos
              </button>
              <button
                @click="sendQuickMessage('¿Cuáles son sus precios?')"
                class="w-full text-left px-3 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all-smooth"
              >
                💰 Consultar precios
              </button>
              <button
                @click="sendQuickMessage('¿Cómo puedo hacer un pedido?')"
                class="w-full text-left px-3 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all-smooth"
              >
                🛒 Proceso de compra
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

export default {
  name: 'EnhancedChat',
  setup() {
    const messages = ref([])
    const textMessage = ref('')
    const messageType = ref('text')
    const isLoading = ref(false)
    const isTyping = ref(false)
    const isRecording = ref(false)
    const selectedAudioFile = ref(null)
    const selectedImageFile = ref(null)
    const imagePreview = ref('')
    const messagesContainer = ref(null)
    const chatId = ref(1)

    // Scroll to bottom
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    // Format time
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Send text message
    const sendTextMessage = async () => {
      if (!textMessage.value.trim() || isLoading.value) return

      const userMessage = {
        id: Date.now(),
        sender: 'user',
        content: textMessage.value,
        message_type: 'text',
        timestamp: new Date().toISOString()
      }

      messages.value.push(userMessage)
      const messageToSend = textMessage.value
      textMessage.value = ''
      isLoading.value = true
      isTyping.value = true

      scrollToBottom()

      try {
        const response = await axios.post('/api/chat-enhanced/message', {
          message: messageToSend,
          chat_id: chatId.value,
          message_type: 'text'
        })

        const botMessage = {
          id: response.data.message_id,
          sender: 'bot',
          content: response.data.response,
          message_type: response.data.message_type,
          recommendations: response.data.recommendations || [],
          image_analysis: response.data.image_analysis,
          timestamp: response.data.timestamp
        }

        messages.value.push(botMessage)
      } catch (error) {
        console.error('Error sending message:', error)
        const errorMessage = {
          id: Date.now(),
          sender: 'bot',
          content: 'Lo siento, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?',
          message_type: 'text',
          timestamp: new Date().toISOString()
        }
        messages.value.push(errorMessage)
      } finally {
        isLoading.value = false
        isTyping.value = false
        scrollToBottom()
      }
    }

    // Handle audio file
    const handleAudioFile = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedAudioFile.value = file
      }
    }

    // Send audio message
    const sendAudioMessage = async () => {
      if (!selectedAudioFile.value || isLoading.value) return

      isLoading.value = true
      isTyping.value = true

      try {
        const formData = new FormData()
        formData.append('audio_file', selectedAudioFile.value)
        formData.append('chat_id', chatId.value)

        const response = await axios.post('/api/chat-enhanced/upload-audio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        const userMessage = {
          id: Date.now(),
          sender: 'user',
          content: `🎤 Audio: ${selectedAudioFile.value.name}`,
          message_type: 'audio',
          timestamp: new Date().toISOString()
        }

        const botMessage = {
          id: response.data.message_id,
          sender: 'bot',
          content: response.data.response,
          message_type: response.data.message_type,
          recommendations: response.data.recommendations || [],
          timestamp: response.data.timestamp
        }

        messages.value.push(userMessage, botMessage)
        selectedAudioFile.value = null
      } catch (error) {
        console.error('Error sending audio:', error)
        const errorMessage = {
          id: Date.now(),
          sender: 'bot',
          content: 'Lo siento, hubo un error procesando tu audio. ¿Podrías intentar de nuevo?',
          message_type: 'text',
          timestamp: new Date().toISOString()
        }
        messages.value.push(errorMessage)
      } finally {
        isLoading.value = false
        isTyping.value = false
        scrollToBottom()
      }
    }

    // Handle image file
    const handleImageFile = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedImageFile.value = file
        const reader = new FileReader()
        reader.onload = (e) => {
          imagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    // Send image message
    const sendImageMessage = async () => {
      if (!selectedImageFile.value || isLoading.value) return

      isLoading.value = true
      isTyping.value = true

      try {
        const formData = new FormData()
        formData.append('image_file', selectedImageFile.value)
        formData.append('chat_id', chatId.value)

        const response = await axios.post('/api/chat-enhanced/upload-image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        const userMessage = {
          id: Date.now(),
          sender: 'user',
          content: `📸 Imagen: ${selectedImageFile.value.name}`,
          message_type: 'image',
          timestamp: new Date().toISOString()
        }

        const botMessage = {
          id: response.data.message_id,
          sender: 'bot',
          content: response.data.response,
          message_type: response.data.message_type,
          recommendations: response.data.recommendations || [],
          image_analysis: response.data.image_analysis,
          timestamp: response.data.timestamp
        }

        messages.value.push(userMessage, botMessage)
        selectedImageFile.value = null
        imagePreview.value = ''
      } catch (error) {
        console.error('Error sending image:', error)
        const errorMessage = {
          id: Date.now(),
          sender: 'bot',
          content: 'Lo siento, hubo un error procesando tu imagen. ¿Podrías intentar de nuevo?',
          message_type: 'text',
          timestamp: new Date().toISOString()
        }
        messages.value.push(errorMessage)
      } finally {
        isLoading.value = false
        isTyping.value = false
        scrollToBottom()
      }
    }

    // Start recording (placeholder)
    const startRecording = () => {
      isRecording.value = !isRecording.value
      // TODO: Implement actual recording functionality
    }

    // Send quick message
    const sendQuickMessage = (message) => {
      textMessage.value = message
      sendTextMessage()
    }

    // Clear chat
    const clearChat = () => {
      messages.value = []
      selectedAudioFile.value = null
      selectedImageFile.value = null
      imagePreview.value = ''
    }

    onMounted(() => {
      // Add welcome message
      const welcomeMessage = {
        id: Date.now(),
        sender: 'bot',
        content: '¡Hola! 👋 Soy tu asistente inteligente. Puedo ayudarte con texto, procesar tus audios y analizar imágenes. ¿En qué puedo asistirte hoy?',
        message_type: 'text',
        timestamp: new Date().toISOString()
      }
      messages.value.push(welcomeMessage)
    })

    return {
      messages,
      textMessage,
      messageType,
      isLoading,
      isTyping,
      isRecording,
      selectedAudioFile,
      selectedImageFile,
      imagePreview,
      messagesContainer,
      sendTextMessage,
      handleAudioFile,
      sendAudioMessage,
      handleImageFile,
      sendImageMessage,
      startRecording,
      sendQuickMessage,
      clearChat,
      formatTime
    }
  }
}
</script>

<style scoped>
/* Estilos adicionales si es necesario */
</style>



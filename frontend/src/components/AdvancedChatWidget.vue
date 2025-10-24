<template>
  <div class="advanced-chat-widget">
    <div class="chat-header">
      <h3>🤖 Asistente Inteligente</h3>
      <div class="status-indicator" :class="{ connected: connected }">
        {{ connected ? '🟢 Conectado' : '🔴 Desconectado' }}
      </div>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" 
           :class="['message', message.sender]">
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          
          <!-- Mostrar contexto adicional si está disponible -->
          <div v-if="message.context" class="message-context">
            <div v-if="message.context.product_mentions?.length" class="context-section">
              <strong>📦 Productos mencionados:</strong>
              <span v-for="mention in message.context.product_mentions" :key="mention" 
                    class="product-mention">{{ mention }}</span>
            </div>
            
            <div v-if="message.context.recommendations?.length" class="context-section">
              <strong>💡 Recomendaciones:</strong>
              <div v-for="rec in message.context.recommendations" :key="rec.product" 
                   class="recommendation">
                {{ rec.product }} - {{ rec.reason }}
              </div>
            </div>
            
            <div v-if="message.context.suggested_actions?.length" class="context-section">
              <strong>🎯 Acciones sugeridas:</strong>
              <span v-for="action in message.context.suggested_actions" :key="action" 
                    class="action-tag">{{ action }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Indicador de escritura -->
      <div v-if="isTyping" class="message bot typing">
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <div class="input-container">
        <input 
          v-model="currentMessage" 
          @keydown.enter="sendMessage"
          placeholder="Pregunta sobre productos, precios, envíos..."
          :disabled="!connected"
          class="message-input"
        />
        <button 
          @click="sendMessage" 
          :disabled="!connected || !currentMessage.trim()"
          class="send-button"
        >
          📤
        </button>
      </div>
      
      <div class="quick-actions">
        <button @click="sendQuickMessage('¿Qué productos tienen?')" class="quick-btn">
          Ver productos
        </button>
        <button @click="sendQuickMessage('¿Cuáles son sus precios?')" class="quick-btn">
          Consultar precios
        </button>
        <button @click="sendQuickMessage('¿Cómo hago un pedido?')" class="quick-btn">
          Cómo pedir
        </button>
      </div>
    </div>
    
    <div class="chat-controls">
      <button @click="connect" :disabled="connected" class="control-btn">
        Conectar
      </button>
      <button @click="disconnect" :disabled="!connected" class="control-btn">
        Desconectar
      </button>
      <button @click="clearChat" class="control-btn">
        Limpiar chat
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

const ws = ref(null)
const connected = ref(false)
const chatId = ref(null)
const currentMessage = ref('')
const messages = ref([])
const isTyping = ref(false)
const messagesContainer = ref(null)

// Conectar al WebSocket
function connect() {
  if (connected.value) return
  
  const wsUrl = (import.meta.env.VITE_API_BASE || 'http://localhost:8000')
    .replace('http', 'ws') + '/ws/support'
  
  ws.value = new WebSocket(wsUrl)
  
  ws.value.onopen = () => {
    connected.value = true
    addSystemMessage('Conectado al asistente inteligente')
  }
  
  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.type === 'chat_opened') {
        chatId.value = data.chat_id
        addSystemMessage(`Chat iniciado (ID: ${data.chat_id})`)
      } else if (data.type === 'bot') {
        isTyping.value = false
        addMessage('bot', data.message, data.context)
      }
    } catch (error) {
      console.error('Error parsing message:', error)
      addMessage('bot', event.data)
    }
  }
  
  ws.value.onclose = () => {
    connected.value = false
    addSystemMessage('Conexión cerrada')
  }
  
  ws.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    addSystemMessage('Error de conexión')
  }
}

// Desconectar
function disconnect() {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
}

// Enviar mensaje
function sendMessage() {
  if (!currentMessage.value.trim() || !connected.value) return
  
  addMessage('user', currentMessage.value)
  ws.value.send(currentMessage.value)
  currentMessage.value = ''
  isTyping.value = true
}

// Enviar mensaje rápido
function sendQuickMessage(message) {
  currentMessage.value = message
  sendMessage()
}

// Agregar mensaje al chat
function addMessage(sender, content, context = null) {
  messages.value.push({
    sender,
    content,
    context,
    timestamp: new Date()
  })
  scrollToBottom()
}

// Agregar mensaje del sistema
function addSystemMessage(content) {
  messages.value.push({
    sender: 'system',
    content,
    timestamp: new Date()
  })
  scrollToBottom()
}

// Limpiar chat
function clearChat() {
  messages.value = []
  chatId.value = null
}

// Hacer scroll hacia abajo
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Formatear tiempo
function formatTime(timestamp) {
  return timestamp.toLocaleTimeString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// Conectar automáticamente al montar
onMounted(() => {
  // No conectar automáticamente, dejar que el usuario decida
})
</script>

<style scoped>
.advanced-chat-widget {
  border: 1px solid #ddd;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  height: 600px;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.status-indicator {
  font-size: 0.9rem;
  opacity: 0.9;
}

.status-indicator.connected {
  opacity: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f8f9fa;
}

.message {
  margin-bottom: 1rem;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.bot {
  justify-content: flex-start;
}

.message.system {
  justify-content: center;
}

.message-content {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  position: relative;
}

.message.user .message-content {
  background: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.bot .message-content {
  background: white;
  color: #333;
  border: 1px solid #e9ecef;
  border-bottom-left-radius: 4px;
}

.message.system .message-content {
  background: #e9ecef;
  color: #6c757d;
  border-radius: 8px;
  font-style: italic;
  text-align: center;
}

.message-text {
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  text-align: right;
}

.message.system .message-time {
  text-align: center;
}

.message-context {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e9ecef;
  font-size: 0.85rem;
}

.context-section {
  margin-bottom: 0.5rem;
}

.context-section:last-child {
  margin-bottom: 0;
}

.product-mention {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin: 0.25rem 0.25rem 0.25rem 0;
  font-size: 0.8rem;
}

.recommendation {
  background: #f3e5f5;
  color: #7b1fa2;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  margin: 0.25rem 0;
  font-size: 0.8rem;
}

.action-tag {
  display: inline-block;
  background: #e8f5e8;
  color: #2e7d32;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin: 0.25rem 0.25rem 0.25rem 0;
  font-size: 0.8rem;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite ease-in-out;
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
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.chat-input {
  padding: 1rem;
  background: white;
  border-top: 1px solid #e9ecef;
}

.input-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
  font-size: 0.9rem;
}

.message-input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.send-button {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #0056b3;
}

.send-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.quick-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
  padding: 0.5rem 0.75rem;
  border-radius: 16px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.chat-controls {
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.control-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s;
}

.control-btn:hover:not(:disabled) {
  background: #5a6268;
}

.control-btn:disabled {
  background: #adb5bd;
  cursor: not-allowed;
}
</style>



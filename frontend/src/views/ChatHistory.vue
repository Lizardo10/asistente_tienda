<template>
  <div class="chat-history-container">
    <!-- Header -->
    <div class="chat-history-header">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h2 class="mb-0">
            <i class="fas fa-comments me-2 text-primary"></i>
            Historial de Conversaciones
          </h2>
          <p class="text-muted mb-0">Gestiona todas las conversaciones del chat</p>
        </div>
        <div class="d-flex gap-2">
          <button @click="refreshData" class="btn btn-outline-primary" :disabled="loading">
            <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': loading }"></i>
            Actualizar
          </button>
          <button @click="showStats = !showStats" class="btn btn-outline-info">
            <i class="fas fa-chart-bar me-1"></i>
            Estadísticas
          </button>
        </div>
      </div>
    </div>

    <!-- Estadísticas -->
    <div v-if="showStats" class="stats-section mb-4">
      <div class="row g-3">
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-primary">
              <i class="fas fa-comments"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.total_conversations }}</h3>
              <p>Conversaciones</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-success">
              <i class="fas fa-message"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.total_messages }}</h3>
              <p>Mensajes</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-warning">
              <i class="fas fa-user"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.registered_conversations }}</h3>
              <p>Usuarios Registrados</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-info">
              <i class="fas fa-user-secret"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.guest_conversations }}</h3>
              <p>Usuarios Guest</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-section mb-4">
      <div class="row g-3">
        <div class="col-md-4">
          <select v-model="filterType" class="form-select">
            <option value="all">Todas las conversaciones</option>
            <option value="registered">Solo usuarios registrados</option>
            <option value="guest">Solo usuarios guest</option>
          </select>
        </div>
        <div class="col-md-4">
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control" 
            placeholder="Buscar por email o chat_id..."
          >
        </div>
        <div class="col-md-4">
          <select v-model="sortBy" class="form-select">
            <option value="recent">Más recientes</option>
            <option value="oldest">Más antiguas</option>
            <option value="messages">Más mensajes</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Lista de conversaciones -->
    <div class="conversations-list">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-2">Cargando conversaciones...</p>
      </div>

      <div v-else-if="filteredConversations.length === 0" class="text-center py-5">
        <i class="fas fa-comments fa-3x text-muted mb-3"></i>
        <h4 class="text-muted">No hay conversaciones</h4>
        <p class="text-muted">Aún no se han registrado conversaciones de chat</p>
      </div>

      <div v-else class="row g-3">
        <div 
          v-for="conversation in filteredConversations" 
          :key="conversation.chat_id"
          class="col-md-6 col-lg-4"
        >
          <div class="conversation-card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <div class="user-avatar me-3">
                  <i class="fas" :class="conversation.user_id ? 'fa-user' : 'fa-user-secret'"></i>
                </div>
                <div>
                  <h6 class="mb-0">{{ conversation.user_email }}</h6>
                  <small class="text-muted">
                    {{ conversation.user_id ? 'Usuario Registrado' : 'Usuario Guest' }}
                  </small>
                </div>
              </div>
              <div class="dropdown">
                <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu">
                  <li>
                    <button @click="viewConversation(conversation.chat_id)" class="dropdown-item">
                      <i class="fas fa-eye me-2"></i>Ver Conversación
                    </button>
                  </li>
                  <li>
                    <button @click="deleteConversation(conversation.chat_id)" class="dropdown-item text-danger">
                      <i class="fas fa-trash me-2"></i>Eliminar
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            
            <div class="card-body">
              <div class="conversation-preview">
                <p class="text-muted small mb-2">
                  <strong>Último mensaje:</strong>
                </p>
                <p class="preview-text">
                  {{ getLastMessage(conversation) }}
                </p>
              </div>
              
              <div class="conversation-stats">
                <div class="row text-center">
                  <div class="col-4">
                    <small class="text-muted">Mensajes</small>
                    <div class="fw-bold">{{ conversation.message_count }}</div>
                  </div>
                  <div class="col-4">
                    <small class="text-muted">Inicio</small>
                    <div class="fw-bold">{{ formatDate(conversation.messages[0]?.created_at) }}</div>
                  </div>
                  <div class="col-4">
                    <small class="text-muted">Última Actividad</small>
                    <div class="fw-bold">{{ formatDate(conversation.last_message) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para ver conversación completa -->
    <div class="modal fade" id="conversationModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-comments me-2"></i>
              Conversación: {{ selectedConversation?.user_email }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedConversation" class="conversation-messages">
              <div 
                v-for="message in selectedConversation.messages" 
                :key="message.id"
                class="message-item"
                :class="message.sender"
              >
                <div class="message-header">
                  <span class="sender-badge" :class="message.sender">
                    <i class="fas" :class="message.sender === 'user' ? 'fa-user' : 'fa-robot'"></i>
                    {{ message.sender === 'user' ? 'Usuario' : 'Bot' }}
                  </span>
                  <span class="message-time">{{ formatDateTime(message.created_at) }}</span>
                </div>
                <div class="message-content">
                  {{ message.content }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            <button 
              @click="deleteConversation(selectedConversation?.chat_id)" 
              class="btn btn-danger"
              data-bs-dismiss="modal"
            >
              <i class="fas fa-trash me-1"></i>Eliminar Conversación
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

// Estado
const conversations = ref([])
const stats = ref({})
const loading = ref(false)
const showStats = ref(false)
const selectedConversation = ref(null)

// Filtros
const filterType = ref('all')
const searchQuery = ref('')
const sortBy = ref('recent')

// Computed
const filteredConversations = computed(() => {
  let filtered = [...conversations.value]
  
  // Filtrar por tipo
  if (filterType.value === 'registered') {
    filtered = filtered.filter(c => c.user_id)
  } else if (filterType.value === 'guest') {
    filtered = filtered.filter(c => !c.user_id)
  }
  
  // Filtrar por búsqueda
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c => 
      c.user_email.toLowerCase().includes(query) ||
      c.chat_id.toLowerCase().includes(query)
    )
  }
  
  // Ordenar
  if (sortBy.value === 'recent') {
    filtered.sort((a, b) => new Date(b.last_message) - new Date(a.last_message))
  } else if (sortBy.value === 'oldest') {
    filtered.sort((a, b) => new Date(a.last_message) - new Date(b.last_message))
  } else if (sortBy.value === 'messages') {
    filtered.sort((a, b) => b.message_count - a.message_count)
  }
  
  return filtered
})

// Métodos
async function loadConversations() {
  try {
    loading.value = true
    const response = await api.get('/admin/chat-history/conversations')
    conversations.value = response.data.conversations
  } catch (error) {
    console.error('Error cargando conversaciones:', error)
    alert('Error cargando conversaciones')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const response = await api.get('/admin/chat-history/stats')
    stats.value = response.data.stats
  } catch (error) {
    console.error('Error cargando estadísticas:', error)
  }
}

async function refreshData() {
  await Promise.all([loadConversations(), loadStats()])
}

async function viewConversation(chatId) {
  try {
    const response = await api.get(`/admin/chat-history/conversations/${chatId}`)
    selectedConversation.value = response.data.conversation
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('conversationModal'))
    modal.show()
  } catch (error) {
    console.error('Error cargando conversación:', error)
    alert('Error cargando conversación')
  }
}

async function deleteConversation(chatId) {
  if (!confirm('¿Estás seguro de eliminar esta conversación?')) return
  
  try {
    await api.delete(`/admin/chat-history/conversations/${chatId}`)
    await loadConversations()
    alert('Conversación eliminada exitosamente')
  } catch (error) {
    console.error('Error eliminando conversación:', error)
    alert('Error eliminando conversación')
  }
}

function getLastMessage(conversation) {
  if (!conversation.messages || conversation.messages.length === 0) return 'Sin mensajes'
  const lastMsg = conversation.messages[conversation.messages.length - 1]
  return lastMsg.content.length > 100 
    ? lastMsg.content.substring(0, 100) + '...'
    : lastMsg.content
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('es-GT')
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('es-GT')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.chat-history-container {
  padding: 2rem;
  background: #f8f9fa;
  min-height: 100vh;
}

.chat-history-header {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.stats-section {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 1rem;
}

.stat-content h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-content p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.conversation-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.conversation-card:hover {
  transform: translateY(-2px);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.preview-text {
  font-size: 0.9rem;
  color: #495057;
  margin: 0;
}

.conversation-stats {
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
  margin-top: 1rem;
}

.conversation-messages {
  max-height: 400px;
  overflow-y: auto;
}

.message-item {
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
}

.message-item.user {
  background: #e3f2fd;
  margin-left: 2rem;
}

.message-item.bot {
  background: #f3e5f5;
  margin-right: 2rem;
}

.message-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.sender-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.sender-badge.user {
  background: #2196f3;
  color: white;
}

.sender-badge.bot {
  background: #9c27b0;
  color: white;
}

.message-time {
  font-size: 0.8rem;
  color: #6c757d;
  margin-left: auto;
}

.message-content {
  font-size: 0.9rem;
  line-height: 1.4;
}
</style>



<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
  <div>
            <h1 class="text-3xl font-bold text-gray-900">Panel de Administración</h1>
            <p class="mt-2 text-gray-600">Gestiona tu tienda desde aquí</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-right">
              <p class="text-sm text-gray-600">Bienvenido</p>
              <p class="font-medium text-gray-900">{{ userEmail }}</p>
            </div>
            <div class="w-10 h-10 bg-gradient-to-r from-orange-500 to-green-500 rounded-full flex items-center justify-center">
              <i class="fas fa-user text-white"></i>
            </div>
          </div>
    </div>
      </div>
    </div>

    <!-- Estadísticas principales -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-lg">
              <i class="fas fa-box text-blue-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Productos</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.totalProducts }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-lg">
              <i class="fas fa-shopping-bag text-green-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Pedidos Hoy</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.ordersToday }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-center">
            <div class="p-3 bg-yellow-100 rounded-lg">
              <i class="fas fa-dollar-sign text-yellow-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Ingresos Hoy</p>
              <p class="text-2xl font-bold text-gray-900">Q{{ stats.revenueToday.toFixed(2) }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-lg">
              <i class="fas fa-users text-purple-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Clientes Activos</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.activeUsers }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Acciones rápidas -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <router-link 
            to="/admin/products" 
            class="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200"
          >
            <i class="fas fa-box text-blue-600 text-xl mr-3"></i>
            <div>
              <p class="font-medium text-gray-900">Gestionar Productos</p>
              <p class="text-sm text-gray-600">Agregar, editar, eliminar</p>
            </div>
          </router-link>
          
          <router-link 
            to="/admin/orders" 
            class="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200"
          >
            <i class="fas fa-shopping-bag text-green-600 text-xl mr-3"></i>
            <div>
              <p class="font-medium text-gray-900">Gestionar Pedidos</p>
              <p class="text-sm text-gray-600">Ver y actualizar estados</p>
            </div>
          </router-link>
          
          <router-link 
            to="/admin/accounting" 
            class="flex items-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors duration-200"
          >
            <i class="fas fa-calculator text-yellow-600 text-xl mr-3"></i>
            <div>
              <p class="font-medium text-gray-900">Contabilidad</p>
              <p class="text-sm text-gray-600">Reportes financieros</p>
            </div>
          </router-link>
          
          <router-link 
            to="/admin/financial" 
            class="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200"
          >
            <i class="fas fa-chart-line text-green-600 text-xl mr-3"></i>
            <div>
              <p class="font-medium text-gray-900">Panel Financiero</p>
              <p class="text-sm text-gray-600">Transacciones e ingresos</p>
            </div>
          </router-link>
          
          <router-link 
            to="/admin/chat-history" 
            class="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors duration-200"
          >
            <i class="fas fa-comments text-purple-600 text-xl mr-3"></i>
            <div>
              <p class="font-medium text-gray-900">Historial de Chat</p>
              <p class="text-sm text-gray-600">Conversaciones con IA</p>
          </div>
          </router-link>
          </div>
      </div>

      <!-- Gráficos y análisis -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Productos más vendidos -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Productos Más Vendidos</h3>
          <div class="space-y-4">
            <div v-for="product in topProducts" :key="product.id" class="flex items-center justify-between">
              <div class="flex items-center">
                <img 
                  :src="resolveImage(product.image_url)" 
                  :alt="product.title"
                  class="w-10 h-10 rounded-lg object-cover mr-3"
                >
                <div>
                  <p class="font-medium text-gray-900">{{ product.title }}</p>
                  <p class="text-sm text-gray-600">{{ product.sales }} ventas</p>
                </div>
              </div>
              <span class="text-sm font-medium text-gray-900">Q{{ product.price.toFixed(2) }}</span>
            </div>
      </div>
    </div>

        <!-- Pedidos recientes -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Pedidos Recientes</h3>
          <div class="space-y-4">
            <div v-for="order in recentOrders" :key="order.id" class="flex items-center justify-between">
              <div>
                <p class="font-medium text-gray-900">Pedido #{{ order.id }}</p>
                <p class="text-sm text-gray-600">{{ order.customer_email }}</p>
              </div>
              <div class="text-right">
                <p class="font-medium text-gray-900">Q{{ order.total_amount.toFixed(2) }}</p>
                <span 
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="getStatusClass(order.status)"
                >
                  {{ getStatusText(order.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actividad reciente -->
      <div class="bg-white rounded-xl shadow-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
        <div class="space-y-4">
          <div v-for="activity in recentActivity" :key="activity.id" class="flex items-center">
            <div class="flex-shrink-0">
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center"
                :class="getActivityClass(activity.type)"
              >
                <i :class="getActivityIcon(activity.type)" class="text-white text-sm"></i>
              </div>
            </div>
            <div class="ml-4 flex-1">
              <p class="text-sm text-gray-900">{{ activity.description }}</p>
              <p class="text-xs text-gray-500">{{ formatTime(activity.created_at) }}</p>
            </div>
          </div>
    </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { session } from '../services/session'
import api from '../services/api'

// Estado reactivo
const stats = ref({
  totalProducts: 0,
  ordersToday: 0,
  revenueToday: 0,
  activeUsers: 0
})

const topProducts = ref([])
const recentOrders = ref([])
const recentActivity = ref([])

// Computed properties
const userEmail = computed(() => session.user?.email || 'Administrador')

// Métodos
async function loadStats() {
  try {
    // Cargar productos
    const productsResponse = await api.get('/products')
    stats.value.totalProducts = productsResponse.data.length

    // Cargar pedidos
    const ordersResponse = await api.get('/orders/admin')
    const today = new Date().toDateString()
    const todayOrders = ordersResponse.data.filter(order => 
      new Date(order.created_at).toDateString() === today
    )
    
    stats.value.ordersToday = todayOrders.length
    stats.value.revenueToday = todayOrders.reduce((total, order) => total + order.total_amount, 0)
    
    // Simular usuarios activos (en una app real vendría del backend)
    stats.value.activeUsers = Math.floor(Math.random() * 50) + 20

    // Productos más vendidos (simulado)
    topProducts.value = productsResponse.data.slice(0, 5).map(product => ({
      ...product,
      sales: Math.floor(Math.random() * 100) + 10
    }))

    // Pedidos recientes
    recentOrders.value = ordersResponse.data.slice(0, 5)

    // Actividad reciente (simulada)
    recentActivity.value = [
      {
        id: 1,
        type: 'order',
        description: 'Nuevo pedido #1234 por Q250.00',
        created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString()
      },
      {
        id: 2,
        type: 'product',
        description: 'Producto "Camisa Azul" actualizado',
        created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString()
      },
      {
        id: 3,
        type: 'user',
        description: 'Nuevo usuario registrado',
        created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
      }
    ]

  } catch (error) {
    console.error('Error cargando estadísticas:', error)
  }
}

function resolveImage(imageUrl) {
  if (!imageUrl) {
    return 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&h=100&fit=crop'
  }
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  return `http://localhost:8000${imageUrl}`
}

function getStatusClass(status) {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    shipped: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

function getStatusText(status) {
  const texts = {
    pending: 'Pendiente',
    processing: 'Procesando',
    shipped: 'Enviado',
    delivered: 'Entregado',
    cancelled: 'Cancelado'
  }
  return texts[status] || status
}

function getActivityClass(type) {
  const classes = {
    order: 'bg-green-500',
    product: 'bg-blue-500',
    user: 'bg-purple-500'
  }
  return classes[type] || 'bg-gray-500'
}

function getActivityIcon(type) {
  const icons = {
    order: 'fas fa-shopping-bag',
    product: 'fas fa-box',
    user: 'fas fa-user'
  }
  return icons[type] || 'fas fa-circle'
}

function formatTime(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return 'Hace un momento'
  if (diff < 3600000) return `Hace ${Math.floor(diff / 60000)} minutos`
  if (diff < 86400000) return `Hace ${Math.floor(diff / 3600000)} horas`
  return date.toLocaleDateString('es-GT')
}

// Cargar datos al montar
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
/* Animaciones suaves */
.transition-shadow {
  transition: box-shadow 0.3s ease-in-out;
}

.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}
</style>
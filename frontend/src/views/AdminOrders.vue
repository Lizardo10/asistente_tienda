<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Gestión de Pedidos</h1>
            <p class="mt-2 text-gray-600">Administra todos los pedidos de la tienda</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Estadísticas -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-lg">
              <i class="fas fa-shopping-bag text-blue-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Pedidos</p>
              <p class="text-2xl font-bold text-gray-900">{{ orders.length }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-yellow-100 rounded-lg">
              <i class="fas fa-clock text-yellow-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Pendientes</p>
              <p class="text-2xl font-bold text-gray-900">{{ pendingOrders }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-lg">
              <i class="fas fa-check-circle text-green-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Completados</p>
              <p class="text-2xl font-bold text-gray-900">{{ completedOrders }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-lg">
              <i class="fas fa-dollar-sign text-purple-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Ingresos Totales</p>
              <p class="text-2xl font-bold text-gray-900">Q{{ totalRevenue.toFixed(2) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div class="flex flex-col lg:flex-row gap-4">
          <div class="flex-1">
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Buscar por cliente o ID de pedido..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
          </div>
          <div class="lg:w-64">
            <select 
              v-model="statusFilter"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="pending">Pendiente</option>
              <option value="processing">Procesando</option>
              <option value="shipped">Enviado</option>
              <option value="delivered">Entregado</option>
              <option value="cancelled">Cancelado</option>
            </select>
          </div>
          <div class="lg:w-48">
            <select 
              v-model="dateFilter"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los días</option>
              <option value="today">Hoy</option>
              <option value="week">Esta semana</option>
              <option value="month">Este mes</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Lista de pedidos -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pedido
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Productos
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="order in filteredOrders" :key="order.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">#{{ order.id }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ order.customer_email }}</div>
                  <div class="text-sm text-gray-500">{{ order.customer_name }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ order.items.length }} producto(s)</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  Q{{ order.total_amount.toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusClass(order.status)"
                  >
                    {{ getStatusText(order.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(order.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button 
                      @click="viewOrder(order)"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    <button 
                      @click="updateOrderStatus(order)"
                      class="text-green-600 hover:text-green-900"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal para ver detalles del pedido -->
    <div v-if="selectedOrder" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              Pedido #{{ selectedOrder.id }}
            </h3>
            <button 
              @click="selectedOrder = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <i class="fas fa-times text-xl"></i>
            </button>
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Información del cliente -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-3">Información del Cliente</h4>
              <div class="space-y-2 text-sm">
                <p><span class="font-medium">Nombre:</span> {{ selectedOrder.customer_name }}</p>
                <p><span class="font-medium">Email:</span> {{ selectedOrder.customer_email }}</p>
                <p><span class="font-medium">Teléfono:</span> {{ selectedOrder.customer_phone || 'No proporcionado' }}</p>
                <p><span class="font-medium">Dirección:</span> {{ selectedOrder.shipping_address }}</p>
              </div>
            </div>
            
            <!-- Información del pedido -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-3">Información del Pedido</h4>
              <div class="space-y-2 text-sm">
                <p><span class="font-medium">Estado:</span> 
                  <span :class="getStatusClass(selectedOrder.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusText(selectedOrder.status) }}
                  </span>
                </p>
                <p><span class="font-medium">Fecha:</span> {{ formatDate(selectedOrder.created_at) }}</p>
                <p><span class="font-medium">Total:</span> Q{{ selectedOrder.total_amount.toFixed(2) }}</p>
                <p><span class="font-medium">Método de pago:</span> {{ selectedOrder.payment_method }}</p>
              </div>
            </div>
          </div>
          
          <!-- Productos del pedido -->
          <div class="mt-6">
            <h4 class="font-medium text-gray-900 mb-3">Productos</h4>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cantidad</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precio</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subtotal</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="item in selectedOrder.items" :key="item.id">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <img 
                          :src="resolveImage(item.image_url)" 
                          :alt="item.title"
                          class="h-10 w-10 rounded-lg object-cover mr-3"
                        >
                        <div>
                          <div class="text-sm font-medium text-gray-900">{{ item.title }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ item.quantity }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      Q{{ item.price.toFixed(2) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      Q{{ (item.price * item.quantity).toFixed(2) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

// Estado reactivo
const orders = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const dateFilter = ref('')
const selectedOrder = ref(null)

// Computed properties
const pendingOrders = computed(() => {
  return orders.value.filter(o => o.status === 'pending').length
})

const completedOrders = computed(() => {
  return orders.value.filter(o => o.status === 'delivered').length
})

const totalRevenue = computed(() => {
  return orders.value.reduce((total, order) => total + order.total_amount, 0)
})

const filteredOrders = computed(() => {
  let filtered = orders.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(o => 
      o.customer_email.toLowerCase().includes(query) ||
      o.customer_name.toLowerCase().includes(query) ||
      o.id.toString().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(o => o.status === statusFilter.value)
  }

  if (dateFilter.value) {
    const now = new Date()
    filtered = filtered.filter(o => {
      const orderDate = new Date(o.created_at)
      switch (dateFilter.value) {
        case 'today':
          return orderDate.toDateString() === now.toDateString()
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          return orderDate >= weekAgo
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          return orderDate >= monthAgo
        default:
          return true
      }
    })
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

// Métodos
async function loadOrders() {
  try {
    const response = await api.get('/orders/admin')
    orders.value = response.data
  } catch (error) {
    console.error('Error cargando pedidos:', error)
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

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('es-GT', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function viewOrder(order) {
  selectedOrder.value = order
}

async function updateOrderStatus(order) {
  const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
  const currentIndex = statuses.indexOf(order.status)
  const nextIndex = (currentIndex + 1) % statuses.length
  const newStatus = statuses[nextIndex]
  
  if (confirm(`¿Cambiar estado del pedido #${order.id} a "${getStatusText(newStatus)}"?`)) {
    try {
      await api.put(`/orders/${order.id}/status`, { status: newStatus })
      await loadOrders()
    } catch (error) {
      console.error('Error actualizando estado:', error)
    }
  }
}

// Cargar datos al montar
onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
/* Animaciones suaves */
.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}
</style>












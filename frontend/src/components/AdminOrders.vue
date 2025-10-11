<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-3">
      <h5 class="mb-0">Historial de Todas las Compras</h5>
      <button class="btn btn-sm btn-outline-secondary" @click="loadOrders">
        <i class="bi bi-arrow-clockwise"></i> Actualizar
      </button>
    </div>

    <div v-if="loading" class="alert alert-info">Cargando órdenes...</div>
    <div v-else-if="!orders.length" class="alert alert-warning">No hay órdenes registradas.</div>

    <div v-else>
      <!-- Resumen -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card text-bg-primary">
            <div class="card-body">
              <h6 class="card-title">Total de Órdenes</h6>
              <h3 class="mb-0">{{ orders.length }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-bg-success">
            <div class="card-body">
              <h6 class="card-title">Ventas Totales</h6>
              <h3 class="mb-0">Q {{ totalSales.toFixed(2) }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-bg-info">
            <div class="card-body">
              <h6 class="card-title">Clientes Únicos</h6>
              <h3 class="mb-0">{{ uniqueCustomers }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros -->
      <div class="card mb-3">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <input 
                v-model="searchQuery" 
                type="text" 
                class="form-control" 
                placeholder="Buscar por email o nombre..."
              />
            </div>
            <div class="col-md-3">
              <select v-model="filterStatus" class="form-select">
                <option value="">Todos los estados</option>
                <option value="pending">Pendiente</option>
                <option value="completed">Completado</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
            <div class="col-md-5 text-end">
              <span class="text-muted">{{ filteredOrders.length }} órdenes mostradas</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabla de órdenes -->
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Cliente</th>
              <th>Email</th>
              <th>Fecha</th>
              <th>Items</th>
              <th>Total</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td><strong>#{{ order.id }}</strong></td>
              <td>{{ order.user?.full_name || 'Sin nombre' }}</td>
              <td>{{ order.user?.email || 'N/A' }}</td>
              <td>
                <small>{{ formatDate(order.created_at) }}</small>
              </td>
              <td class="text-center">{{ order.items.length }}</td>
              <td>
                <strong>Q {{ calculateTotal(order.items).toFixed(2) }}</strong>
              </td>
              <td>
                <span :class="getStatusBadgeClass(order.status)">
                  {{ getStatusLabel(order.status) }}
                </span>
              </td>
              <td>
                <button 
                  class="btn btn-sm btn-outline-primary" 
                  @click="viewDetails(order)"
                >
                  Ver Detalles
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de detalles -->
    <div v-if="selectedOrder" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Detalles de Orden #{{ selectedOrder.id }}</h5>
            <button type="button" class="btn-close" @click="closeDetails"></button>
          </div>
          <div class="modal-body">
            <!-- Info del cliente -->
            <div class="card mb-3">
              <div class="card-body">
                <h6 class="card-title">Información del Cliente</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-1"><strong>Nombre:</strong> {{ selectedOrder.user?.full_name || 'Sin nombre' }}</p>
                    <p class="mb-1"><strong>Email:</strong> {{ selectedOrder.user?.email || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-1"><strong>Fecha:</strong> {{ formatDate(selectedOrder.created_at) }}</p>
                    <p class="mb-1">
                      <strong>Estado:</strong> 
                      <span :class="getStatusBadgeClass(selectedOrder.status)">
                        {{ getStatusLabel(selectedOrder.status) }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Productos -->
            <div class="card">
              <div class="card-body">
                <h6 class="card-title">Productos</h6>
                <ul class="list-group">
                  <li 
                    class="list-group-item d-flex justify-content-between align-items-center"
                    v-for="item in selectedOrder.items" 
                    :key="item.product_id"
                  >
                    <div class="d-flex align-items-center" style="gap:.75rem;">
                      <img 
                        :src="resolveImage(getProductImage(item.product_id))" 
                        alt="" 
                        style="width:48px;height:48px;object-fit:cover;border-radius:.25rem;"
                      />
                      <div>
                        <div class="fw-semibold">{{ getProductTitle(item.product_id) }}</div>
                        <div class="text-muted small">
                          Q {{ Number(item.price_each).toFixed(2) }} × {{ item.quantity }}
                        </div>
                      </div>
                    </div>
                    <strong>Q {{ (Number(item.price_each) * Number(item.quantity)).toFixed(2) }}</strong>
                  </li>
                </ul>
                <div class="d-flex justify-content-between mt-3 pt-3 border-top">
                  <strong>Total:</strong>
                  <strong class="fs-5">Q {{ calculateTotal(selectedOrder.items).toFixed(2) }}</strong>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDetails">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Orders, Products } from '../services/api'
import api from '../services/api'

const orders = ref([])
const products = ref([])
const loading = ref(true)
const selectedOrder = ref(null)
const searchQuery = ref('')
const filterStatus = ref('')

const PLACEHOLDER_IMG = 'https://via.placeholder.com/600x400?text=Producto'

function resolveImage(u) {
  if (!u) return PLACEHOLDER_IMG
  if (!/^https?:\/\//i.test(u)) {
    const base = (api?.defaults?.baseURL || '').replace(/\/$/, '')
    return base + u
  }
  return u
}

// Cálculos
const totalSales = computed(() => {
  return orders.value.reduce((sum, order) => sum + calculateTotal(order.items), 0)
})

const uniqueCustomers = computed(() => {
  const userIds = new Set(orders.value.map(o => o.user_id))
  return userIds.size
})

const filteredOrders = computed(() => {
  let result = orders.value

  // Filtrar por búsqueda
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(order => 
      order.user?.email?.toLowerCase().includes(query) ||
      order.user?.full_name?.toLowerCase().includes(query)
    )
  }

  // Filtrar por estado
  if (filterStatus.value) {
    result = result.filter(order => order.status === filterStatus.value)
  }

  return result
})

function calculateTotal(items) {
  return (items || []).reduce((sum, item) => 
    sum + Number(item.price_each || 0) * Number(item.quantity || 1), 0
  )
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('es-GT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return iso || ''
  }
}

function getStatusLabel(status) {
  const labels = {
    pending: 'Pendiente',
    completed: 'Completado',
    cancelled: 'Cancelado'
  }
  return labels[status] || status
}

function getStatusBadgeClass(status) {
  const classes = {
    pending: 'badge bg-warning text-dark',
    completed: 'badge bg-success',
    cancelled: 'badge bg-danger'
  }
  return classes[status] || 'badge bg-secondary'
}

function getProductById(id) {
  return products.value.find(p => p.id === id)
}

function getProductTitle(id) {
  return getProductById(id)?.title || `Producto ${id}`
}

function getProductImage(id) {
  const p = getProductById(id)
  return p?.image_url || p?.images?.[0]?.url || ''
}

function viewDetails(order) {
  selectedOrder.value = order
}

function closeDetails() {
  selectedOrder.value = null
}

async function loadOrders() {
  loading.value = true
  try {
    // Cargar productos para mostrar info
    const { data: prods } = await Products.list()
    products.value = Array.isArray(prods) ? prods : []

    // Cargar todas las órdenes (admin)
    const { data } = await Orders.all()
    orders.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('Error cargando órdenes:', e)
    alert(e?.response?.data?.detail || 'Error al cargar las órdenes')
  } finally {
    loading.value = false
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.modal.show {
  display: block;
}
</style>




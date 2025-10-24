<template>
  <div class="accounting-dashboard">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <h2 class="mb-0">
            <i class="fas fa-calculator me-2"></i>
            Área Contable
          </h2>
          <p class="text-muted">Gestión de inventario y reportes financieros</p>
        </div>
      </div>

      <!-- Estadísticas principales -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="card-title">${{ formatCurrency(stats.total_sales_today) }}</h4>
                  <p class="card-text">Ventas Hoy</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-dollar-sign fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="card-title">{{ stats.total_orders_today }}</h4>
                  <p class="card-text">Pedidos Hoy</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-shopping-cart fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="card-title">{{ stats.low_stock_products }}</h4>
                  <p class="card-text">Stock Bajo</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-exclamation-triangle fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card bg-danger text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="card-title">{{ stats.out_of_stock_products }}</h4>
                  <p class="card-text">Sin Stock</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-times-circle fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs de navegación -->
      <ul class="nav nav-tabs" id="accountingTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="inventory-tab" data-bs-toggle="tab" data-bs-target="#inventory" type="button" role="tab">
            <i class="fas fa-boxes me-2"></i>Inventario
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="transactions-tab" data-bs-toggle="tab" data-bs-target="#transactions" type="button" role="tab">
            <i class="fas fa-exchange-alt me-2"></i>Transacciones
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button" role="tab">
            <i class="fas fa-chart-bar me-2"></i>Reportes
          </button>
        </li>
      </ul>

      <!-- Contenido de las tabs -->
      <div class="tab-content" id="accountingTabsContent">
        <!-- Tab Inventario -->
        <div class="tab-pane fade show active" id="inventory" role="tabpanel">
          <div class="row mt-4">
            <div class="col-12">
              <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                  <h5 class="mb-0">Control de Inventario</h5>
                  <button class="btn btn-primary" @click="showAdjustStockModal = true">
                    <i class="fas fa-plus me-2"></i>Ajustar Stock
                  </button>
                </div>
                <div class="card-body">
                  <div class="table-responsive">
                    <table class="table table-striped">
                      <thead>
                        <tr>
                          <th>Producto</th>
                          <th>Stock Actual</th>
                          <th>Mínimo</th>
                          <th>Máximo</th>
                          <th>Estado</th>
                          <th>Última Actualización</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="item in stockLevels" :key="item.id">
                          <td>{{ item.product_name }}</td>
                          <td>{{ item.current_stock }}</td>
                          <td>{{ item.min_stock_level }}</td>
                          <td>{{ item.max_stock_level }}</td>
                          <td>
                            <span :class="getStockStatusClass(item.status)" class="badge">
                              {{ getStockStatusText(item.status) }}
                            </span>
                          </td>
                          <td>{{ formatDate(item.last_updated) }}</td>
                          <td>
                            <button class="btn btn-sm btn-outline-primary" @click="editStock(item)">
                              <i class="fas fa-edit"></i>
                            </button>
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

        <!-- Tab Transacciones -->
        <div class="tab-pane fade" id="transactions" role="tabpanel">
          <div class="row mt-4">
            <div class="col-12">
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">Transacciones Recientes</h5>
                </div>
                <div class="card-body">
                  <div class="table-responsive">
                    <table class="table table-striped">
                      <thead>
                        <tr>
                          <th>Producto</th>
                          <th>Tipo</th>
                          <th>Cantidad</th>
                          <th>Costo Total</th>
                          <th>Administrador</th>
                          <th>Fecha</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="transaction in stats.recent_transactions" :key="transaction.id">
                          <td>{{ transaction.product_name }}</td>
                          <td>
                            <span class="badge" :class="getTransactionTypeClass(transaction.transaction_type)">
                              {{ getTransactionTypeText(transaction.transaction_type) }}
                            </span>
                          </td>
                          <td>{{ transaction.quantity }}</td>
                          <td>${{ formatCurrency(transaction.total_cost) }}</td>
                          <td>{{ transaction.admin_email }}</td>
                          <td>{{ formatDate(transaction.created_at) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab Reportes -->
        <div class="tab-pane fade" id="reports" role="tabpanel">
          <div class="row mt-4">
            <div class="col-md-6">
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">Productos Más Vendidos</h5>
                </div>
                <div class="card-body">
                  <div class="list-group">
                    <div v-for="product in stats.top_selling_products" :key="product.name" class="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <strong>{{ product.name }}</strong>
                        <br>
                        <small class="text-muted">{{ product.total_sold }} unidades vendidas</small>
                      </div>
                      <span class="badge bg-primary rounded-pill">${{ formatCurrency(product.total_revenue) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">Resumen Financiero</h5>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-6">
                      <p><strong>Valor Total Inventario:</strong></p>
                      <h4 class="text-primary">${{ formatCurrency(stats.total_inventory_value) }}</h4>
                    </div>
                    <div class="col-6">
                      <p><strong>Total Clientes:</strong></p>
                      <h4 class="text-success">{{ stats.total_customers }}</h4>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para ajustar stock -->
    <div class="modal fade" id="adjustStockModal" tabindex="-1" v-if="showAdjustStockModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Ajustar Stock</h5>
            <button type="button" class="btn-close" @click="showAdjustStockModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="adjustStock">
              <div class="mb-3">
                <label class="form-label">Producto</label>
                <select v-model="adjustmentForm.product_id" class="form-select" required>
                  <option value="">Seleccionar producto</option>
                  <option v-for="item in stockLevels" :key="item.id" :value="item.product_id">
                    {{ item.product_name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Nueva Cantidad</label>
                <input v-model.number="adjustmentForm.new_quantity" type="number" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Razón del Ajuste</label>
                <textarea v-model="adjustmentForm.reason" class="form-control" rows="3" required></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showAdjustStockModal = false">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="adjustStock" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Ajustar Stock
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Accounting } from '../services/api'

// Estado reactivo
const stats = ref({})
const stockLevels = ref([])
const loading = ref(false)
const showAdjustStockModal = ref(false)

const adjustmentForm = ref({
  product_id: '',
  new_quantity: 0,
  reason: ''
})

// Métodos
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // Cargar estadísticas del dashboard
    const statsResponse = await Accounting.getDashboardStats()
    stats.value = statsResponse.data
    
    // Cargar niveles de stock
    const stockResponse = await Accounting.getStockLevels()
    stockLevels.value = stockResponse.data
    
  } catch (error) {
    console.error('Error cargando datos del dashboard:', error)
    alert('Error cargando datos del dashboard')
  } finally {
    loading.value = false
  }
}

const adjustStock = async () => {
  try {
    loading.value = true
    
    await Accounting.adjustStock(adjustmentForm.value)
    
    // Recargar datos
    await loadDashboardData()
    
    // Limpiar formulario y cerrar modal
    adjustmentForm.value = {
      product_id: '',
      new_quantity: 0,
      reason: ''
    }
    showAdjustStockModal.value = false
    
    alert('Stock ajustado correctamente')
    
  } catch (error) {
    console.error('Error ajustando stock:', error)
    alert('Error ajustando stock')
  } finally {
    loading.value = false
  }
}

const editStock = (item) => {
  adjustmentForm.value.product_id = item.product_id
  adjustmentForm.value.new_quantity = item.current_stock
  showAdjustStockModal.value = true
}

// Utilidades
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(amount)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('es-GT')
}

const getStockStatusClass = (status) => {
  switch (status) {
    case 'out_of_stock': return 'bg-danger'
    case 'low_stock': return 'bg-warning'
    case 'in_stock': return 'bg-success'
    default: return 'bg-secondary'
  }
}

const getStockStatusText = (status) => {
  switch (status) {
    case 'out_of_stock': return 'Sin Stock'
    case 'low_stock': return 'Stock Bajo'
    case 'in_stock': return 'En Stock'
    default: return 'Desconocido'
  }
}

const getTransactionTypeClass = (type) => {
  switch (type) {
    case 'sale': return 'bg-success'
    case 'purchase': return 'bg-primary'
    case 'adjustment': return 'bg-warning'
    case 'return': return 'bg-info'
    case 'damage': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getTransactionTypeText = (type) => {
  switch (type) {
    case 'sale': return 'Venta'
    case 'purchase': return 'Compra'
    case 'adjustment': return 'Ajuste'
    case 'return': return 'Devolución'
    case 'damage': return 'Daño'
    default: return 'Desconocido'
  }
}

// Ciclo de vida
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.accounting-dashboard {
  padding: 20px;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.nav-tabs .nav-link {
  border: none;
  border-bottom: 2px solid transparent;
}

.nav-tabs .nav-link.active {
  border-bottom-color: #007bff;
  background-color: transparent;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.badge {
  font-size: 0.75em;
}
</style>

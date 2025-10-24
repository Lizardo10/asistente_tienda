<template>
  <div class="admin-financial-dashboard">
    <div class="dashboard-header">
      <h1 class="dashboard-title">
        <i class="fas fa-chart-line"></i>
        Panel Financiero
      </h1>
      <div class="dashboard-actions">
        <button @click="refreshData" class="btn-refresh" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          Actualizar
        </button>
        <button @click="exportReport" class="btn-export">
          <i class="fas fa-download"></i>
          Exportar Reporte
        </button>
      </div>
    </div>

    <!-- Estadísticas Principales -->
    <div class="stats-grid">
      <div class="stat-card revenue">
        <div class="stat-icon">
          <i class="fas fa-dollar-sign"></i>
        </div>
        <div class="stat-content">
          <h3>Ingresos Totales</h3>
          <p class="stat-value">Q{{ formatCurrency(stats.total_revenue) }}</p>
          <p class="stat-change positive">
            <i class="fas fa-arrow-up"></i>
            Q{{ formatCurrency(stats.revenue_this_month) }} este mes
          </p>
        </div>
      </div>

      <div class="stat-card orders">
        <div class="stat-icon">
          <i class="fas fa-shopping-cart"></i>
        </div>
        <div class="stat-content">
          <h3>Total Órdenes</h3>
          <p class="stat-value">{{ stats.total_orders }}</p>
          <p class="stat-change positive">
            <i class="fas fa-arrow-up"></i>
            {{ stats.orders_this_month }} este mes
          </p>
        </div>
      </div>

      <div class="stat-card transactions">
        <div class="stat-icon">
          <i class="fas fa-credit-card"></i>
        </div>
        <div class="stat-content">
          <h3>Transacciones</h3>
          <p class="stat-value">{{ stats.total_transactions }}</p>
          <p class="stat-change">
            <span class="success">{{ stats.successful_transactions }} exitosas</span>
            <span class="failed">{{ stats.failed_transactions }} fallidas</span>
          </p>
        </div>
      </div>

      <div class="stat-card conversion">
        <div class="stat-icon">
          <i class="fas fa-percentage"></i>
        </div>
        <div class="stat-content">
          <h3>Tasa de Conversión</h3>
          <p class="stat-value">{{ stats.conversion_rate.toFixed(1) }}%</p>
          <p class="stat-change">
            Valor promedio: Q{{ formatCurrency(stats.average_order_value) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Gráficos y Tablas -->
    <div class="dashboard-content">
      <!-- Filtros -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Período:</label>
          <select v-model="selectedPeriod" @change="loadData">
            <option value="today">Hoy</option>
            <option value="week">Esta Semana</option>
            <option value="month">Este Mes</option>
            <option value="year">Este Año</option>
            <option value="custom">Personalizado</option>
          </select>
        </div>
        
        <div class="filter-group" v-if="selectedPeriod === 'custom'">
          <label>Desde:</label>
          <input type="date" v-model="customStartDate" @change="loadData">
          <label>Hasta:</label>
          <input type="date" v-model="customEndDate" @change="loadData">
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="{ active: activeTab === tab.id }"
          class="tab-button"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <!-- Contenido de Tabs -->
      <div class="tab-content">
        <!-- Transacciones -->
        <div v-if="activeTab === 'transactions'" class="tab-panel">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Orden</th>
                  <th>Método</th>
                  <th>Monto</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="transaction in transactions" :key="transaction.id">
                  <td>{{ transaction.id }}</td>
                  <td>#{{ transaction.order_id }}</td>
                  <td>
                    <span class="payment-method">
                      <i class="fab fa-paypal" v-if="transaction.payment_method === 'paypal'"></i>
                      {{ transaction.payment_method }}
                    </span>
                  </td>
                  <td>Q{{ formatCurrency(transaction.amount) }}</td>
                  <td>
                    <span :class="['status-badge', transaction.status]">
                      {{ getStatusText(transaction.status) }}
                    </span>
                  </td>
                  <td>{{ formatDate(transaction.created_at) }}</td>
                  <td>
                    <button 
                      @click="viewTransaction(transaction.id)"
                      class="btn-action"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Órdenes -->
        <div v-if="activeTab === 'orders'" class="tab-panel">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Cliente</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Pago</th>
                  <th>Fecha</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in orders" :key="order.id">
                  <td>#{{ order.id }}</td>
                  <td>Usuario #{{ order.user_id }}</td>
                  <td>Q{{ formatCurrency(order.total_amount) }}</td>
                  <td>
                    <span :class="['status-badge', order.status]">
                      {{ getStatusText(order.status) }}
                    </span>
                  </td>
                  <td>
                    <span :class="['status-badge', order.payment_status]">
                      {{ getStatusText(order.payment_status) }}
                    </span>
                  </td>
                  <td>{{ formatDate(order.created_at) }}</td>
                  <td>
                    <button 
                      @click="viewOrder(order.id)"
                      class="btn-action"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Reportes -->
        <div v-if="activeTab === 'reports'" class="tab-panel">
          <div class="reports-section">
            <h3>Reporte de Ingresos</h3>
            <div class="report-filters">
              <div class="filter-group">
                <label>Agrupar por:</label>
                <select v-model="reportGroupBy" @change="generateReport">
                  <option value="day">Día</option>
                  <option value="week">Semana</option>
                  <option value="month">Mes</option>
                </select>
              </div>
            </div>
            
            <div v-if="reportData" class="report-results">
              <div class="report-summary">
                <div class="summary-item">
                  <span class="label">Ingresos Totales:</span>
                  <span class="value">Q{{ formatCurrency(reportData.summary.total_revenue) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Comisiones:</span>
                  <span class="value">Q{{ formatCurrency(reportData.summary.total_fees) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Ingresos Netos:</span>
                  <span class="value">Q{{ formatCurrency(reportData.summary.net_revenue) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Transacciones:</span>
                  <span class="value">{{ reportData.summary.total_transactions }}</span>
                </div>
              </div>
              
              <div class="report-chart">
                <!-- Aquí podrías agregar un gráfico con Chart.js o similar -->
                <div class="chart-placeholder">
                  <i class="fas fa-chart-bar"></i>
                  <p>Gráfico de ingresos por {{ reportGroupBy }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

// Estado reactivo
const loading = ref(false)
const stats = ref({})
const transactions = ref([])
const orders = ref([])
const reportData = ref(null)
const activeTab = ref('transactions')
const selectedPeriod = ref('month')
const customStartDate = ref('')
const customEndDate = ref('')
const reportGroupBy = ref('day')

// Tabs disponibles
const tabs = [
  { id: 'transactions', label: 'Transacciones', icon: 'fas fa-credit-card' },
  { id: 'orders', label: 'Órdenes', icon: 'fas fa-shopping-cart' },
  { id: 'reports', label: 'Reportes', icon: 'fas fa-chart-bar' }
]

// Métodos
const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadDashboardStats(),
      loadTransactions(),
      loadOrders()
    ])
  } catch (error) {
    console.error('Error cargando datos:', error)
  } finally {
    loading.value = false
  }
}

const loadDashboardStats = async () => {
  try {
    const response = await api.get('/admin/financial/dashboard')
    stats.value = response.data
  } catch (error) {
    console.error('Error cargando estadísticas:', error)
  }
}

const loadTransactions = async () => {
  try {
    const response = await api.get('/admin/financial/transactions', {
      params: {
        limit: 50,
        status: selectedPeriod.value === 'today' ? null : undefined
      }
    })
    transactions.value = response.data
  } catch (error) {
    console.error('Error cargando transacciones:', error)
  }
}

const loadOrders = async () => {
  try {
    const response = await api.get('/admin/financial/orders', {
      params: {
        limit: 50
      }
    })
    orders.value = response.data
  } catch (error) {
    console.error('Error cargando órdenes:', error)
  }
}

const generateReport = async () => {
  try {
    const startDate = getStartDate()
    const endDate = getEndDate()
    
    const response = await api.get('/admin/financial/revenue-report', {
      params: {
        start_date: startDate,
        end_date: endDate,
        group_by: reportGroupBy.value
      }
    })
    reportData.value = response.data
  } catch (error) {
    console.error('Error generando reporte:', error)
  }
}

const getStartDate = () => {
  if (selectedPeriod.value === 'custom') {
    return customStartDate.value
  }
  
  const now = new Date()
  switch (selectedPeriod.value) {
    case 'today':
      return now.toISOString().split('T')[0]
    case 'week':
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      return weekAgo.toISOString().split('T')[0]
    case 'month':
      return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]
    case 'year':
      return new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0]
    default:
      return now.toISOString().split('T')[0]
  }
}

const getEndDate = () => {
  if (selectedPeriod.value === 'custom') {
    return customEndDate.value
  }
  return new Date().toISOString().split('T')[0]
}

const refreshData = () => {
  loadData()
}

const exportReport = () => {
  // Implementar exportación de reportes
  console.log('Exportar reporte')
}

const viewTransaction = (transactionId) => {
  console.log('Ver transacción:', transactionId)
}

const viewOrder = (orderId) => {
  console.log('Ver orden:', orderId)
}

const formatCurrency = (amount) => {
  return Number(amount || 0).toFixed(2)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-GT')
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': 'Pendiente',
    'completed': 'Completado',
    'failed': 'Fallido',
    'refunded': 'Reembolsado',
    'cancelled': 'Cancelado'
  }
  return statusMap[status] || status
}

// Inicialización
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-financial-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e5e7eb;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dashboard-actions {
  display: flex;
  gap: 10px;
}

.btn-refresh, .btn-export {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-refresh {
  background: #3b82f6;
  color: white;
}

.btn-refresh:hover:not(:disabled) {
  background: #2563eb;
}

.btn-export {
  background: #10b981;
  color: white;
}

.btn-export:hover {
  background: #059669;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-card.revenue .stat-icon {
  background: linear-gradient(135deg, #10b981, #059669);
}

.stat-card.orders .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.stat-card.transactions .stat-icon {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.stat-card.conversion .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-content h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.stat-change {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-change.positive {
  color: #10b981;
}

.filters-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.tabs {
  display: flex;
  background: white;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tab-button {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: #f9fafb;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab-button:hover {
  background: #f3f4f6;
}

.tab-button.active {
  background: white;
  color: #3b82f6;
  border-bottom: 3px solid #3b82f6;
}

.tab-content {
  background: white;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.tab-panel {
  padding: 20px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.refunded {
  background: #e0e7ff;
  color: #3730a3;
}

.payment-method {
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-action {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.btn-action:hover {
  background: #f3f4f6;
  color: #374151;
}

.reports-section h3 {
  margin-bottom: 20px;
  color: #1f2937;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-item {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.summary-item .label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
}

.chart-placeholder {
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.chart-placeholder i {
  font-size: 48px;
  margin-bottom: 10px;
  display: block;
}

.fa-spin {
  animation: fa-spin 1s infinite linear;
}

@keyframes fa-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

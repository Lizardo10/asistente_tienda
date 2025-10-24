import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000'
})

// token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// -------------------
// Productos
// -------------------
export const Products = {
  list() {
    return api.get('/products')
  },
  listAll() {
    return api.get('/products/all')  // Solo para administradores
  },
  get(id) {
    return api.get(`/products/${id}`)
  },
  create(payload) {
    return api.post('/products', payload)           // 👈 necesario
  },
  update(id, payload) {
    return api.put(`/products/${id}`, payload)
  },
  remove(id) {
    return api.delete(`/products/${id}`)
  },
  listImages(id) {
    return api.get(`/products/${id}/images`)
  },
  uploadImage(id, file) {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/products/${id}/images`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  removeImage(id, imageId) {
    return api.delete(`/products/${id}/images/${imageId}`)
  },
}

// -------------------
// Auth (opcional)
// -------------------
export const Auth = {
  register(payload) { return api.post('/auth-complete/register', payload) },
  login(payload)    { return api.post('/auth-complete/login', payload) },
  me()              { return api.get('/auth-complete/me') },
  requestReset(email) { return api.post('/auth-complete/password-reset-request', { email }) },
  confirmReset(token, newPassword) { return api.post('/auth-complete/password-reset-confirm', { token, new_password: newPassword }) },
  confirmAccount(token) { return api.post('/auth-complete/confirm-email', { token }) },
  resendConfirmation(email) { return api.post('/auth-complete/resend-confirmation', { email }) }
}


export const Orders = {
  create(payload) {
    return api.post('/orders', payload)
  },
  my() {
    return api.get('/orders/my')
  },
  detail(id) {
    return api.get(`/orders/${id}`)
  },
  // Admin: obtener todas las órdenes
  all() {
    return api.get('/orders')
  }
}

// -------------------
// Accounting (Solo Admin)
// -------------------
export const Accounting = {
  // Dashboard
  getDashboardStats() {
    return api.get('/admin/accounting/dashboard')
  },
  
  // Inventario
  getStockLevels() {
    return api.get('/admin/accounting/inventory/stock-levels')
  },
  
  getLowStockProducts() {
    return api.get('/admin/accounting/inventory/low-stock')
  },
  
  adjustStock(payload) {
    return api.post('/admin/accounting/inventory/adjust-stock', payload)
  },
  
  createInventoryTransaction(payload) {
    return api.post('/admin/accounting/inventory/transaction', payload)
  },
  
  // Reportes
  generateFinancialReport(reportType, periodStart, periodEnd) {
    return api.post('/admin/accounting/reports/generate', {
      report_type: reportType,
      period_start: periodStart,
      period_end: periodEnd
    })
  },
  
  getFinancialReports() {
    return api.get('/admin/accounting/reports')
  },
  
  // Utilidades
  initializeProductStock(productId, initialStock = 0) {
    return api.post(`/admin/accounting/inventory/initialize/${productId}`, {
      initial_stock: initialStock
    })
  }
}


export default api

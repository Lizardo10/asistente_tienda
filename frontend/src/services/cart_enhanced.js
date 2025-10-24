import { reactive, computed, watch } from 'vue'

const saved = JSON.parse(localStorage.getItem('cart') || '[]')

export const cart = reactive({
  items: saved // [{id,title,price,image_url,quantity}]
})

export const count = computed(() => cart.items.reduce((a,b) => a + (b.quantity||0), 0))
export const total = computed(() => cart.items.reduce((a,b) => a + Number(b.price||0) * Number(b.quantity||1), 0))

// Sistema de notificaciones
export const notifications = reactive({
  items: []
})

// Sistema de actualizaciones en tiempo real
export const realTimeUpdates = reactive({
  isProcessing: false,
  lastUpdate: null,
  connectionStatus: 'disconnected'
})

watch(() => cart.items, (v) => {
  localStorage.setItem('cart', JSON.stringify(v))
  // Notificar cambio en tiempo real
  notifyCartUpdate()
}, { deep: true })

export function add(product, qty = 1) {
  const id = product.id
  const existing = cart.items.find(it => it.id === id)
  if (existing) {
    existing.quantity += qty
    addNotification('success', `Agregado ${qty} más de "${product.title}"`)
  } else {
    cart.items.push({ 
      id, 
      title: product.title, 
      price: product.price, 
      image_url: product.image_url || (product.images?.[0]?.url ?? ''), 
      quantity: qty 
    })
    addNotification('success', `"${product.title}" agregado al carrito`)
  }
  notifyCartUpdate()
}

export function remove(id) {
  const idx = cart.items.findIndex(it => it.id === id)
  if (idx !== -1) {
    const item = cart.items[idx]
    cart.items.splice(idx, 1)
    addNotification('info', `"${item.title}" removido del carrito`)
    notifyCartUpdate()
  }
}

export function clear() {
  cart.items.splice(0, cart.items.length)
  addNotification('info', 'Carrito vaciado')
  notifyCartUpdate()
}

export function updateQuantity(id, newQuantity) {
  const item = cart.items.find(it => it.id === id)
  if (item) {
    const oldQuantity = item.quantity
    item.quantity = Math.max(1, newQuantity)
    
    if (oldQuantity !== item.quantity) {
      addNotification('info', `Cantidad de "${item.title}" actualizada`)
      notifyCartUpdate()
    }
  }
}

export function toOrderPayload() {
  return {
    items: cart.items.map(item => ({
      product_id: item.id,
      quantity: item.quantity
    }))
  }
}

// Sistema de notificaciones
export function addNotification(type, message, duration = 3000) {
  const notification = {
    id: Date.now() + Math.random(),
    type, // 'success', 'error', 'info', 'warning'
    message,
    timestamp: new Date()
  }
  
  notifications.items.push(notification)
  
  // Auto-remove notification after duration
  setTimeout(() => {
    removeNotification(notification.id)
  }, duration)
}

export function removeNotification(id) {
  const idx = notifications.items.findIndex(n => n.id === id)
  if (idx !== -1) {
    notifications.items.splice(idx, 1)
  }
}

export function clearNotifications() {
  notifications.items.splice(0, notifications.items.length)
}

// Sistema de actualizaciones en tiempo real
export function notifyCartUpdate() {
  realTimeUpdates.lastUpdate = new Date()
  
  // Simular actualización en tiempo real
  if (typeof window !== 'undefined' && window.EventSource) {
    // Aquí podrías implementar Server-Sent Events o WebSockets
    console.log('Cart updated:', cart.items.length, 'items')
  }
}

export function setProcessingStatus(isProcessing) {
  realTimeUpdates.isProcessing = isProcessing
  
  if (isProcessing) {
    addNotification('info', 'Procesando compra...')
  } else {
    addNotification('success', 'Compra completada exitosamente')
  }
}

export function setConnectionStatus(status) {
  realTimeUpdates.connectionStatus = status
  
  if (status === 'connected') {
    addNotification('success', 'Conectado al servidor')
  } else if (status === 'disconnected') {
    addNotification('warning', 'Desconectado del servidor')
  }
}

// Funciones para simular actualizaciones en tiempo real
export function simulateRealTimeUpdate() {
  // Simular actualización de stock
  cart.items.forEach(item => {
    // Aquí podrías hacer una llamada al servidor para verificar stock
    console.log(`Checking stock for ${item.title}`)
  })
}

// Funciones de utilidad
export function getCartSummary() {
  return {
    itemCount: count.value,
    totalAmount: total.value,
    items: cart.items.map(item => ({
      id: item.id,
      title: item.title,
      quantity: item.quantity,
      price: item.price,
      subtotal: item.price * item.quantity
    }))
  }
}

export function validateCart() {
  const errors = []
  
  if (cart.items.length === 0) {
    errors.push('El carrito está vacío')
  }
  
  cart.items.forEach(item => {
    if (item.quantity <= 0) {
      errors.push(`Cantidad inválida para "${item.title}"`)
    }
    if (!item.price || item.price <= 0) {
      errors.push(`Precio inválido para "${item.title}"`)
    }
  })
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

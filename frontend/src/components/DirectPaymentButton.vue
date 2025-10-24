<!-- Boton de Pago Directo con Tarjeta -->
<template>
  <div class="direct-payment-container">
    <button 
      @click="payWithCard" 
      :disabled="loading || !cartItems.length"
      class="direct-payment-button"
    >
      <div v-if="loading" class="loading">
        <i class="fas fa-spinner fa-spin"></i>
        Procesando...
      </div>
      <div v-else class="payment-content">
        <i class="fas fa-credit-card"></i>
        Pagar con Tarjeta
      </div>
    </button>
    
    <!-- Modal de confirmación -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirmar Pago</h3>
          <button @click="closeModal" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="payment-summary">
            <h4>Resumen del Pago</h4>
            <div class="summary-item" v-for="item in cartItems" :key="item.id">
              <span>{{ item.title }}</span>
              <span>Q{{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
            <div class="summary-total">
              <span><strong>Total:</strong></span>
              <span><strong>Q{{ totalAmount.toFixed(2) }}</strong></span>
            </div>
          </div>
          
          <div class="payment-info">
            <p><i class="fas fa-info-circle"></i> El pago se procesará descontando de tu saldo disponible</p>
            <p><strong>Saldo actual:</strong> Q{{ userBalance.toFixed(2) }}</p>
            <p><strong>Saldo después del pago:</strong> Q{{ (userBalance - totalAmount).toFixed(2) }}</p>
          </div>
          
          <div v-if="userBalance < totalAmount" class="insufficient-funds">
            <i class="fas fa-exclamation-triangle"></i>
            <p>Saldo insuficiente. Necesitas Q{{ (totalAmount - userBalance).toFixed(2) }} más.</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="cancel-button">
            Cancelar
          </button>
          <button 
            @click="confirmPayment" 
            :disabled="userBalance < totalAmount || processing"
            class="confirm-button"
          >
            <i v-if="processing" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-check"></i>
            {{ processing ? 'Procesando...' : 'Confirmar Pago' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { cart, setProcessingStatus, addNotification } from '../services/cart_enhanced'

const props = defineProps({
  cartItems: {
    type: Array,
    required: true
  },
  userBalance: {
    type: Number,
    default: 1000 // Saldo por defecto
  }
})

const emit = defineEmits(['payment-success', 'payment-error'])

const loading = ref(false)
const processing = ref(false)
const showModal = ref(false)

const totalAmount = computed(() => {
  return props.cartItems.reduce((total, item) => {
    return total + (item.price * item.quantity)
  }, 0)
})

async function payWithCard() {
  if (!props.cartItems.length) {
    addNotification('warning', 'El carrito está vacío')
    return
  }
  
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function confirmPayment() {
  if (props.userBalance < totalAmount.value) {
    addNotification('error', 'Saldo insuficiente')
    return
  }
  
  processing.value = true
  setProcessingStatus(true)
  
  try {
    // 1. Crear orden
    const orderResponse = await createOrder()
    const orderId = orderResponse.order_id
    
    // 2. Procesar pago directo
    const paymentResponse = await processDirectPayment(orderId)
    
    if (paymentResponse.status === 'success') {
      addNotification('success', 'Pago procesado exitosamente')
      emit('payment-success', paymentResponse)
      closeModal()
    } else {
      throw new Error(paymentResponse.message || 'Error procesando pago')
    }
    
  } catch (error) {
    console.error('Error en pago directo:', error)
    addNotification('error', 'Error procesando el pago')
    emit('payment-error', error)
  } finally {
    processing.value = false
    setProcessingStatus(false)
  }
}

async function createOrder() {
  const token = localStorage.getItem('token')
  const response = await fetch('http://localhost:8000/checkout-sqlalchemy/create-order', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      items: props.cartItems.map(item => ({
        product_id: item.id,
        quantity: item.quantity
      }))
    })
  })
  
  if (!response.ok) {
    throw new Error('Error creando orden')
  }
  
  return await response.json()
}

async function processDirectPayment(orderId) {
  const token = localStorage.getItem('token')
  const response = await fetch('http://localhost:8000/checkout-sqlalchemy/direct-payment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      order_id: orderId
    })
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Error procesando pago')
  }
  
  return await response.json()
}
</script>

<style scoped>
.direct-payment-container {
  margin: 20px 0;
}

.direct-payment-button {
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  max-width: 300px;
  transition: background-color 0.3s;
}

.direct-payment-button:hover:not(:disabled) {
  background: #047857;
}

.direct-payment-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.payment-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
}

.close-button:hover {
  background: #f3f4f6;
}

.modal-body {
  padding: 20px;
}

.payment-summary {
  margin-bottom: 20px;
}

.payment-summary h4 {
  margin: 0 0 15px 0;
  color: #1f2937;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 2px solid #e5e7eb;
  margin-top: 10px;
  font-size: 18px;
}

.payment-info {
  background: #f8fafc;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.payment-info p {
  margin: 5px 0;
  color: #374151;
}

.insufficient-funds {
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 15px;
  border-radius: 8px;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.cancel-button {
  flex: 1;
  padding: 12px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-button:hover {
  background: #f9fafb;
}

.confirm-button {
  flex: 1;
  padding: 12px;
  border: none;
  background: #059669;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.confirm-button:hover:not(:disabled) {
  background: #047857;
}

.confirm-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>

<template>
  <div class="checkout-success-page">
    <div class="success-container">
      <div class="success-icon">
        <i class="fas fa-check-circle"></i>
      </div>
      
      <h1 class="success-title">¡Pago Exitoso!</h1>
      <p class="success-message">Tu pedido ha sido procesado correctamente.</p>
      
      <div v-if="orderId" class="order-info">
        <p><strong>ID de Orden:</strong> #{{ orderId }}</p>
        <p><strong>Estado:</strong> <span class="status-completed">Completado</span></p>
      </div>
      
      <div class="success-actions">
        <router-link to="/" class="btn-primary">
          <i class="fas fa-home"></i>
          Volver al Inicio
        </router-link>
        <router-link to="/orders" class="btn-secondary">
          <i class="fas fa-list"></i>
          Ver Mis Pedidos
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import { cart } from '../services/cart'

const route = useRoute()
const orderId = ref(null)

onMounted(async () => {
  // Obtener parámetros de PayPal
  const paymentId = route.query.paymentId
  const payerId = route.query.PayerID
  
  if (paymentId && payerId) {
    try {
      // Ejecutar pago
      const response = await api.post('/checkout-sqlalchemy/paypal/execute', {
        payment_id: paymentId,
        payer_id: payerId
      })
      
      orderId.value = response.data.order_id
      
      // Limpiar carrito
      cart.clear()
      
    } catch (error) {
      console.error('Error ejecutando pago:', error)
    }
  }
})
</script>

<style scoped>
.checkout-success-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.success-container {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.success-icon {
  font-size: 80px;
  color: #10b981;
  margin-bottom: 20px;
}

.success-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 10px;
}

.success-message {
  font-size: 1.2rem;
  color: #6b7280;
  margin-bottom: 30px;
}

.order-info {
  background: #f9fafb;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  text-align: left;
}

.order-info p {
  margin: 10px 0;
  font-size: 1.1rem;
}

.status-completed {
  color: #10b981;
  font-weight: bold;
}

.success-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
  transform: translateY(-2px);
}

@media (max-width: 640px) {
  .success-container {
    padding: 30px 20px;
  }
  
  .success-title {
    font-size: 2rem;
  }
  
  .success-actions {
    flex-direction: column;
  }
  
  .btn-primary, .btn-secondary {
    justify-content: center;
  }
}
</style>
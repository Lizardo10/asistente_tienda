<template>
  <div class="checkout-page">
    <div class="checkout-container">
      <h1 class="checkout-title">Finalizar Compra</h1>
      
      <!-- Resumen del carrito -->
      <div class="cart-summary">
        <h2>Resumen del Pedido</h2>
        <div v-for="item in cart.items" :key="item.id" class="cart-item">
          <div class="item-info">
            <img 
              :src="item.image_url || '/placeholder-product.jpg'" 
              :alt="item.title"
              class="item-image"
            >
            <div class="item-details">
              <h3>{{ item.title }}</h3>
              <p>Q{{ item.price }} x {{ item.quantity }}</p>
            </div>
          </div>
          <div class="item-total">
            Q{{ (item.price * item.quantity).toFixed(2) }}
          </div>
        </div>
        
        <div class="cart-total">
          <h3>Total: Q{{ cartTotal.toFixed(2) }}</h3>
        </div>
      </div>

      <!-- Información de envío -->
      <div class="shipping-info">
        <h2>Información de Envío</h2>
        <div class="form-group">
          <label>Dirección:</label>
          <input 
            v-model="shippingAddress" 
            type="text" 
            placeholder="Ingresa tu dirección completa"
            class="form-input"
          >
        </div>
        <div class="form-group">
          <label>Teléfono:</label>
          <input 
            v-model="shippingPhone" 
            type="tel" 
            placeholder="Número de teléfono"
            class="form-input"
          >
        </div>
      </div>

      <!-- Método de pago -->
      <div class="payment-method">
        <h2>Método de Pago</h2>
        <div class="payment-options">
          <div class="payment-option">
            <input 
              type="radio" 
              id="paypal" 
              value="paypal" 
              v-model="paymentMethod"
            >
            <label for="paypal" class="payment-label">
              <i class="fab fa-paypal"></i>
              PayPal
            </label>
          </div>
        </div>
      </div>

      <!-- Botón de pago -->
      <div class="checkout-actions">
        <button 
          @click="processPayment" 
          :disabled="processing || !canProcessPayment"
          class="paypal-button"
        >
          <i class="fas fa-credit-card"></i>
          {{ processing ? 'Procesando...' : 'Pagar con PayPal' }}
        </button>
        
        <router-link to="/cart" class="back-to-cart">
          <i class="fas fa-arrow-left"></i>
          Volver al Carrito
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { cart } from '../services/cart'
import api from '../services/api'

const router = useRouter()

// Estado reactivo
const processing = ref(false)
const shippingAddress = ref('')
const shippingPhone = ref('')
const paymentMethod = ref('paypal')

// Computed
const cartTotal = computed(() => {
  return cart.items.reduce((total, item) => {
    return total + (item.price * item.quantity)
  }, 0)
})

const canProcessPayment = computed(() => {
  return cart.items.length > 0 && 
         shippingAddress.value.trim() && 
         shippingPhone.value.trim() &&
         paymentMethod.value
})

// Métodos
async function processPayment() {
  if (!canProcessPayment.value) {
    alert('Por favor completa todos los campos requeridos')
    return
  }

  processing.value = true

  try {
    // 1. Crear orden
    const orderResponse = await api.post('/checkout-sqlalchemy/create-order', {
      items: cart.items.map(item => ({
        product_id: item.id,
        quantity: item.quantity
      })),
      shipping_address: shippingAddress.value,
      shipping_phone: shippingPhone.value
    })

    const orderId = orderResponse.data.order_id

    // 2. Crear pago en PayPal
    const paymentResponse = await api.post('/checkout-sqlalchemy/paypal/create-payment', {
      order_id: orderId
    })

    // 3. Redirigir a PayPal
    window.location.href = paymentResponse.data.approval_url

  } catch (error) {
    console.error('Error procesando pago:', error)
    alert('Error procesando el pago. Inténtalo de nuevo.')
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.checkout-page {
  min-height: 100vh;
  background: #f9fafb;
  padding: 20px;
}

.checkout-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.checkout-title {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  padding: 30px 30px 0 30px;
  margin-bottom: 20px;
}

.cart-summary,
.shipping-info,
.payment-method {
  padding: 0 30px 30px 30px;
  border-bottom: 1px solid #e5e7eb;
}

.cart-summary h2,
.shipping-info h2,
.payment-method h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f3f4f6;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.item-details h3 {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 5px;
}

.item-details p {
  color: #6b7280;
  font-size: 0.9rem;
}

.item-total {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

.cart-total {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #e5e7eb;
  text-align: right;
}

.cart-total h3 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.payment-options {
  display: flex;
  gap: 20px;
}

.payment-option {
  display: flex;
  align-items: center;
}

.payment-option input[type="radio"] {
  margin-right: 10px;
}

.payment-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  padding: 12px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.payment-label:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.payment-option input[type="radio"]:checked + .payment-label {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.checkout-actions {
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.paypal-button {
  background: #0070ba;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s;
  min-width: 200px;
  justify-content: center;
}

.paypal-button:hover:not(:disabled) {
  background: #005ea6;
  transform: translateY(-2px);
}

.paypal-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.back-to-cart {
  color: #6b7280;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: color 0.2s;
}

.back-to-cart:hover {
  color: #374151;
}

@media (max-width: 640px) {
  .checkout-page {
    padding: 10px;
  }
  
  .checkout-container {
    border-radius: 8px;
  }
  
  .checkout-title {
    font-size: 1.5rem;
    padding: 20px 20px 0 20px;
  }
  
  .cart-summary,
  .shipping-info,
  .payment-method {
    padding: 0 20px 20px 20px;
  }
  
  .checkout-actions {
    padding: 20px;
  }
  
  .item-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .item-image {
    width: 50px;
    height: 50px;
  }
}
</style>
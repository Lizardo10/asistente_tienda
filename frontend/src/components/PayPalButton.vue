<!-- Boton de PayPal Simple -->
<template>
  <div class="paypal-button-container">
    <button 
      @click="payWithPayPal" 
      :disabled="loading"
      class="paypal-button"
    >
      <div v-if="loading" class="loading">
        Procesando...
      </div>
      <div v-else class="paypal-content">
        <img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg" alt="PayPal" class="paypal-logo">
        Pagar con PayPal
      </div>
    </button>
  </div>
</template>

<script>
export default {
  name: 'PayPalButton',
  props: {
    cartItems: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      loading: false
    }
  },
  methods: {
    async payWithPayPal() {
      if (!this.cartItems || this.cartItems.length === 0) {
        alert('El carrito está vacío')
        return
      }

      this.loading = true

      try {
        // 1. Crear orden
        const orderResponse = await this.createOrder()
        const orderId = orderResponse.order_id

        // 2. Crear pago PayPal
        const paymentResponse = await this.createPayPalPayment(orderId)
        const approvalUrl = paymentResponse.approval_url

        // 3. Redirigir a PayPal
        window.location.href = approvalUrl

      } catch (error) {
        console.error('Error en PayPal:', error)
        alert('Error procesando el pago. Intenta nuevamente.')
      } finally {
        this.loading = false
      }
    },

    async createOrder() {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/checkout-sqlalchemy/create-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          items: this.cartItems.map(item => ({
            product_id: item.id,
            quantity: item.quantity
          }))
        })
      })

      if (!response.ok) {
        throw new Error('Error creando orden')
      }

      return await response.json()
    },

    async createPayPalPayment(orderId) {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/checkout-sqlalchemy/paypal/create-payment', {
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
        throw new Error('Error creando pago PayPal')
      }

      return await response.json()
    }
  }
}
</script>

<style scoped>
.paypal-button-container {
  margin: 20px 0;
}

.paypal-button {
  background: #0070ba;
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

.paypal-button:hover:not(:disabled) {
  background: #005ea6;
}

.paypal-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.paypal-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.paypal-logo {
  height: 20px;
  width: auto;
}

.loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading::after {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid #fff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>










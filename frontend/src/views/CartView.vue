<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sistema de notificaciones -->
    <NotificationSystem />
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 class="text-3xl font-bold text-gray-900">Tu Carrito</h1>
        <p class="text-gray-600 mt-2">Revisa tus productos antes de finalizar la compra</p>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="!cart.items.length" class="text-center py-12">
        <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <i class="fas fa-shopping-cart text-3xl text-gray-400"></i>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Tu carrito está vacío</h3>
        <p class="text-gray-600 mb-6">Agrega algunos productos para comenzar tu compra</p>
        <router-link 
          to="/products" 
          class="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          Ver Productos
        </router-link>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Lista de productos -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border">
            <div class="p-6 border-b">
              <h2 class="text-lg font-semibold text-gray-900">Productos en tu carrito</h2>
            </div>
            <div class="divide-y">
              <div
                v-for="item in cart.items"
                :key="item.id"
                class="p-6 flex items-center space-x-4"
              >
                <img
                  :src="resolveImage(item.image_url || item.images?.[0]?.url)"
                  :alt="item.title"
                  class="w-20 h-20 object-cover rounded-lg"
                />
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-medium text-gray-900 truncate">{{ item.title }}</h3>
                  <p class="text-sm text-gray-500">Precio unitario: Q{{ item.price.toFixed(2) }}</p>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="flex items-center border rounded-lg">
                    <button 
                      @click="updateQuantity(item.id, item.quantity - 1)"
                      class="p-2 hover:bg-gray-100 transition-colors"
                      :disabled="item.quantity <= 1"
                    >
                      <i class="fas fa-minus text-gray-600"></i>
                    </button>
                    <input 
                      type="number" 
                      min="1" 
                      v-model.number="item.quantity"
                      class="w-16 text-center border-0 focus:ring-0"
                    />
                    <button 
                      @click="updateQuantity(item.id, item.quantity + 1)"
                      class="p-2 hover:bg-gray-100 transition-colors"
                    >
                      <i class="fas fa-plus text-gray-600"></i>
                    </button>
                  </div>
                  <div class="text-right">
                    <p class="text-lg font-semibold text-gray-900">
                      Q{{ (item.price * item.quantity).toFixed(2) }}
                    </p>
                  </div>
                  <button 
                    @click="remove(item.id)"
                    class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Resumen de compra -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm border sticky top-8">
            <div class="p-6 border-b">
              <h2 class="text-lg font-semibold text-gray-900">Resumen de compra</h2>
            </div>
            <div class="p-6 space-y-4">
              <div class="flex justify-between">
                <span class="text-gray-600">Subtotal</span>
                <span class="font-medium">Q{{ total.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Envío</span>
                <span class="font-medium text-green-600">Gratis</span>
              </div>
              <div class="border-t pt-4">
                <div class="flex justify-between">
                  <span class="text-lg font-semibold text-gray-900">Total</span>
                  <span class="text-lg font-semibold text-gray-900">Q{{ total.toFixed(2) }}</span>
                </div>
              </div>
              
              <!-- Botones de checkout -->
              <div class="space-y-3 pt-4">
                <PayPalButton :cart-items="cart.items" />
                
                <div class="text-center text-sm text-gray-500">
                  <i class="fas fa-shield-alt mr-1"></i>
                  Pago seguro con PayPal
                </div>
              </div>
              
              <p class="text-xs text-gray-500 text-center mt-4">
                <i class="fas fa-shield-alt mr-1"></i>
                Compra segura y protegida
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { cart, count, total, clear, remove, toOrderPayload, updateQuantity as updateCartQuantity } from '../services/cart'
import { Orders } from '../services/api'
import { useRouter } from 'vue-router'
import PayPalButton from '../components/PayPalButton.vue'
import NotificationSystem from '../components/NotificationSystem.vue'

const router = useRouter()
const processing = ref(false)
const userBalance = ref(1000) // Saldo por defecto

const PLACEHOLDER_IMG = 'https://via.placeholder.com/600x400?text=Producto'

function resolveImage(u) {
  if (!u) return PLACEHOLDER_IMG
  if (!/^https?:\/\//i.test(u)) {
    const base = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/$/, '')
    return base + u
  }
  return u
}

function updateQuantity(productId, newQuantity) {
  if (newQuantity < 1) return
  updateCartQuantity(productId, newQuantity)
}

async function checkoutWithPayPal() {
  if (processing.value) return
  
  try {
    processing.value = true
    
    // Crear orden en el backend
    const payload = toOrderPayload()
    const orderResponse = await Orders.create(payload)
    
    // Crear pago PayPal
    const paymentResponse = await fetch(`${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/checkout-sqlalchemy/paypal/create-payment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        order_id: orderResponse.data.id
      })
    })
    
    if (!paymentResponse.ok) {
      throw new Error('Error creando pago PayPal')
    }
    
    const paymentData = await paymentResponse.json()
    
    // Redirigir a PayPal
    if (paymentData.approval_url) {
      window.location.href = paymentData.approval_url
    } else {
      throw new Error('URL de PayPal no disponible')
    }
    
  } catch (error) {
    console.error('Error en checkout PayPal:', error)
    alert(error?.response?.data?.detail || error.message || 'Error al procesar el pago con PayPal')
  } finally {
    processing.value = false
  }
}

async function checkoutSimple() {
  if (processing.value) return
  
  try {
    processing.value = true
    const payload = toOrderPayload()       
    await Orders.create(payload)
    clear()
    alert('¡Compra realizada con éxito!')
    router.push('/orders')
  } catch (e) {
    console.error('checkout error:', e)
    alert(e?.response?.data?.detail || 'Error al procesar la compra')
  } finally {
    processing.value = false
  }
}

// Manejar éxito de pago PayPal
function handlePaymentSuccess(paymentData) {
  console.log('Pago PayPal exitoso:', paymentData)
  
  // Limpiar carrito
  clear()
  
  // Redirigir a página de éxito
  router.push('/checkout/success')
}

// Manejar error de pago PayPal
function handlePaymentError(error) {
  console.error('Error en pago PayPal:', error)
  // El componente de notificaciones ya maneja el error
}
</script>

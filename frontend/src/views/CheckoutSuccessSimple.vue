<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
      <!-- Icono de éxito -->
      <div class="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
        <i class="fas fa-check text-2xl text-green-600"></i>
      </div>
      
      <!-- Título -->
      <h1 class="text-2xl font-bold text-gray-900 mb-4">¡Pago Exitoso!</h1>
      
      <!-- Mensaje -->
      <p class="text-gray-600 mb-6">
        Tu pedido ha sido procesado correctamente. Recibirás un email de confirmación pronto.
      </p>
      
      <!-- Detalles del pago -->
      <div v-if="paymentId" class="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 class="font-semibold text-gray-900 mb-2">Detalles del Pago</h3>
        <p class="text-sm text-gray-600">ID: {{ paymentId }}</p>
        <p class="text-sm text-gray-600">Estado: Completado</p>
      </div>
      
      <!-- Botones de acción -->
      <div class="space-y-3">
        <router-link 
          to="/products" 
          class="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors inline-block"
        >
          Continuar Comprando
        </router-link>
        
        <router-link 
          to="/orders" 
          class="w-full bg-gray-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors inline-block"
        >
          Ver Mis Pedidos
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const paymentId = ref(null)

onMounted(() => {
  // Obtener parámetros de PayPal de la URL
  paymentId.value = route.query.paymentId || route.query.PayerID || 'N/A'
  
  console.log('Página de éxito cargada')
  console.log('Payment ID:', paymentId.value)
  console.log('Token:', route.query.token)
  console.log('Payer ID:', route.query.PayerID)
})
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>

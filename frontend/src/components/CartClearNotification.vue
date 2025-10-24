<template>
  <div class="cart-clear-notification" v-if="showNotification">
    <div class="notification-content">
      <div class="notification-icon">✅</div>
      <div class="notification-text">
        <h3>¡Compra exitosa!</h3>
        <p>{{ notificationMessage }}</p>
        <p>Orden #{{ orderId }} procesada correctamente</p>
      </div>
      <button @click="clearNotification" class="close-btn">×</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { cart } from '../services/cart'

export default {
  name: 'CartClearNotification',
  setup() {
    const showNotification = ref(false)
    const notificationMessage = ref('')
    const orderId = ref(null)
    let websocket = null

    const clearNotification = () => {
      showNotification.value = false
      notificationMessage.value = ''
      orderId.value = null
    }

    const handleCartCleared = (data) => {
      console.log('Carrito limpiado:', data)
      notificationMessage.value = data.message || 'Carrito limpiado exitosamente'
      orderId.value = data.order_id
      showNotification.value = true
      
      // Limpiar el carrito local
      cart.clear()
      
      // Ocultar notificación después de 5 segundos
      setTimeout(() => {
        clearNotification()
      }, 5000)
    }

    const connectWebSocket = () => {
      // Obtener el ID del usuario desde el token o localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      const userId = user.id || 1 // Fallback para pruebas
      
      const wsUrl = `ws://localhost:8000/realtime/ws/${userId}`
      
      try {
        websocket = new WebSocket(wsUrl)
        
        websocket.onopen = () => {
          console.log('WebSocket conectado para notificaciones del carrito')
        }
        
        websocket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            console.log('Mensaje recibido:', message)
            
            if (message.type === 'cart_cleared') {
              handleCartCleared(message.data)
            } else if (message.type === 'order_completed') {
              // También manejar cuando se completa una orden
              handleCartCleared({
                message: 'Orden completada exitosamente',
                order_id: message.data.order_id
              })
            }
          } catch (error) {
            console.error('Error procesando mensaje WebSocket:', error)
          }
        }
        
        websocket.onclose = () => {
          console.log('WebSocket desconectado')
          // Reconectar después de 3 segundos
          setTimeout(connectWebSocket, 3000)
        }
        
        websocket.onerror = (error) => {
          console.error('Error WebSocket:', error)
        }
      } catch (error) {
        console.error('Error conectando WebSocket:', error)
      }
    }

    onMounted(() => {
      connectWebSocket()
    })

    onUnmounted(() => {
      if (websocket) {
        websocket.close()
      }
    })

    return {
      showNotification,
      notificationMessage,
      orderId,
      clearNotification
    }
  }
}
</script>

<style scoped>
.cart-clear-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
}

.notification-content {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 15px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
}

.notification-text h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.notification-text p {
  margin: 4px 0;
  font-size: 14px;
  opacity: 0.9;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .cart-clear-notification {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .notification-content {
    padding: 15px;
  }
  
  .notification-text h3 {
    font-size: 16px;
  }
  
  .notification-text p {
    font-size: 13px;
  }
}
</style>

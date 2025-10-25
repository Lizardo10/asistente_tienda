<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-gradient-primary">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
            <!-- Header con gradiente -->
            <div class="card-header bg-gradient-primary text-white text-center py-4">
              <div class="mb-3">
                <i class="fas fa-envelope-open-text fa-3x"></i>
              </div>
              <h3 class="mb-0 fw-bold">Confirma tu cuenta</h3>
              <p class="mb-0 opacity-75">Verifica tu email para activar tu cuenta</p>
            </div>

            <!-- Contenido -->
            <div class="card-body p-4">
              <div v-if="!confirmed && !error" class="text-center">
                <!-- Estado: Esperando confirmación -->
                <div class="mb-4">
                  <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                  <h5 class="text-muted">Verificando tu cuenta...</h5>
                  <p class="text-muted small">
                    Por favor espera mientras verificamos tu token de confirmación.
                  </p>
                </div>

                <!-- Información del usuario -->
                <div class="alert alert-info border-0 rounded-3">
                  <div class="d-flex align-items-center">
                    <i class="fas fa-info-circle text-primary me-2"></i>
                    <div>
                      <strong>Email:</strong> {{ userEmail || 'Cargando...' }}<br>
                      <small class="text-muted">Revisa tu bandeja de entrada y spam</small>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="confirmed" class="text-center">
                <!-- Estado: Confirmado exitosamente -->
                <div class="mb-4">
                  <div class="success-icon mb-3">
                    <i class="fas fa-check-circle text-success fa-4x"></i>
                  </div>
                  <h4 class="text-success fw-bold">¡Cuenta confirmada!</h4>
                  <p class="text-muted">
                    Tu cuenta ha sido activada exitosamente. Serás redirigido automáticamente en unos segundos.
                  </p>
                </div>

                <div class="d-grid gap-2">
                  <router-link to="/login" class="btn btn-primary btn-lg rounded-3">
                    <i class="fas fa-sign-in-alt me-2"></i>
                    Iniciar Sesión
                  </router-link>
                  <router-link to="/" class="btn btn-outline-secondary rounded-3">
                    <i class="fas fa-home me-2"></i>
                    Ir al Inicio
                  </router-link>
                </div>
              </div>

              <div v-else-if="error" class="text-center">
                <!-- Estado: Error -->
                <div class="mb-4">
                  <div class="error-icon mb-3">
                    <i class="fas fa-exclamation-triangle text-danger fa-4x"></i>
                  </div>
                  <h4 class="text-danger fw-bold">Error de confirmación</h4>
                  <p class="text-muted">
                    {{ errorMessage }}
                  </p>
                </div>

                <div class="d-grid gap-2">
                  <button @click="resendConfirmation" class="btn btn-primary btn-lg rounded-3" :disabled="resending">
                    <i class="fas fa-paper-plane me-2"></i>
                    <span v-if="!resending">Reenviar Confirmación</span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Enviando...
                    </span>
                  </button>
                  <router-link to="/register" class="btn btn-outline-secondary rounded-3">
                    <i class="fas fa-user-plus me-2"></i>
                    Registrarse Nuevamente
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="card-footer bg-light text-center py-3">
              <small class="text-muted">
                <i class="fas fa-shield-alt me-1"></i>
                Tu información está protegida y segura
              </small>
            </div>
          </div>

          <!-- Información adicional -->
          <div class="text-center mt-4">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="d-flex align-items-center justify-content-center text-white">
                  <i class="fas fa-clock me-2"></i>
                  <small>Confirmación rápida</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="d-flex align-items-center justify-content-center text-white">
                  <i class="fas fa-lock me-2"></i>
                  <small>100% seguro</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="d-flex align-items-center justify-content-center text-white">
                  <i class="fas fa-headset me-2"></i>
                  <small>Soporte 24/7</small>
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Auth } from '../services/api'

const route = useRoute()
const router = useRouter()

const confirmed = ref(false)
const error = ref(false)
const errorMessage = ref('')
const userEmail = ref('')
const resending = ref(false)

async function confirmAccount() {
  try {
    const token = route.query.token
    if (!token) {
      throw new Error('Token de confirmación no encontrado')
    }

    const response = await Auth.confirmAccount(token)
    
    // El backend devuelve un TokenResponse con access_token
    if (response.data && response.data.access_token) {
      // Guardar el token para login automático
      localStorage.setItem('token', response.data.access_token)
      
      confirmed.value = true
      userEmail.value = response.data.user?.email || 'Usuario confirmado'
      
      // Redirigir automáticamente después de un breve delay
      setTimeout(() => {
        router.push('/products')
      }, 2000)
    } else {
      throw new Error('Respuesta inválida del servidor')
    }
  } catch (err) {
    console.error('Error confirmando cuenta:', err)
    error.value = true
    errorMessage.value = err.response?.data?.detail || err.message || 'Error inesperado al confirmar la cuenta'
  }
}

async function resendConfirmation() {
  try {
    resending.value = true
    const email = route.query.email || userEmail.value
    
    if (!email) {
      throw new Error('Email no encontrado')
    }

    await Auth.resendConfirmation(email)
    alert('Email de confirmación reenviado. Revisa tu bandeja de entrada.')
  } catch (err) {
    console.error('Error reenviando confirmación:', err)
    alert('Error al reenviar confirmación: ' + err.message)
  } finally {
    resending.value = false
  }
}

onMounted(() => {
  confirmAccount()
})
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #ff8c00 0%, #32cd32 100%);
  background-size: 400% 400%;
  animation: gradientShift 8s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.success-icon {
  animation: bounceIn 0.6s ease-out;
}

.error-icon {
  animation: shake 0.6s ease-out;
}

@keyframes bounceIn {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

.card {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}
</style>

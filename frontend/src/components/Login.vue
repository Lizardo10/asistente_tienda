<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4">
          <i class="fas fa-store text-white text-2xl"></i>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">Bienvenido de vuelta</h2>
        <p class="mt-2 text-sm text-gray-600">
          Inicia sesión en tu cuenta para continuar
        </p>
      </div>

      <!-- Formulario -->
      <div class="bg-white py-8 px-6 shadow-xl rounded-2xl">
        <form @submit.prevent="submit" class="space-y-6">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Correo electrónico
            </label>
            <div class="relative">
              <input
                id="email"
                v-model.trim="email"
                type="email"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                placeholder="tu@email.com"
              >
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <i class="fas fa-envelope text-gray-400"></i>
              </div>
            </div>
          </div>

          <!-- Contraseña -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                placeholder="Tu contraseña"
              >
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Recordar y olvidar contraseña -->
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember"
                v-model="rememberMe"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <label for="remember" class="ml-2 block text-sm text-gray-700">
                Recordarme
              </label>
            </div>
            <router-link
              to="/reset-password"
              class="text-sm text-blue-600 hover:text-blue-500 font-medium"
            >
              ¿Olvidaste tu contraseña?
            </router-link>
          </div>

          <!-- Error -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <i class="fas fa-exclamation-circle text-red-400"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Botón de envío -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <span v-if="loading" class="flex items-center">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Iniciando sesión...
            </span>
            <span v-else class="flex items-center">
              <i class="fas fa-sign-in-alt mr-2"></i>
              Iniciar Sesión
            </span>
          </button>
        </form>

        <!-- Divider -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">¿No tienes cuenta?</span>
            </div>
          </div>
        </div>

        <!-- Link a registro -->
        <div class="mt-6 text-center">
          <router-link
            to="/register"
            class="inline-flex items-center px-6 py-3 border border-gray-300 rounded-xl text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
          >
            <i class="fas fa-user-plus mr-2"></i>
            Crear cuenta nueva
          </router-link>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center">
        <p class="text-xs text-gray-500">
          Al iniciar sesión, aceptas nuestros
          <a href="#" class="text-blue-600 hover:text-blue-500">Términos de Servicio</a>
          y
          <a href="#" class="text-blue-600 hover:text-blue-500">Política de Privacidad</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Auth } from '../services/api'

// Estado reactivo
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

// Método de envío
async function submit() {
  error.value = ''
  
  if (!email.value || !password.value) {
    error.value = 'Por favor completa todos los campos'
    return
  }
  
  loading.value = true
  
  try {
    const { data } = await Auth.login({ 
      email: email.value, 
      password: password.value 
    })
    
    localStorage.setItem('token', data.access_token)
    
    // Redirigir al home
    window.location.href = '/'
    
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Animaciones suaves */
.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
}

.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Gradientes personalizados */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

/* Efectos hover */
.hover\:from-blue-700:hover {
  --tw-gradient-from: #1d4ed8;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(29, 78, 216, 0));
}

.hover\:to-purple-700:hover {
  --tw-gradient-to: #7c3aed;
}
</style>
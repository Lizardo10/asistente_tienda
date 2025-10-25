<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-white to-green-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-gradient-to-r from-orange-500 to-green-500 rounded-full flex items-center justify-center mb-4">
          <i class="fas fa-user-plus text-white text-2xl"></i>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">Crear cuenta nueva</h2>
        <p class="mt-2 text-sm text-gray-600">
          Únete a nuestra tienda y descubre productos increíbles
        </p>
      </div>

      <!-- Formulario -->
      <div class="bg-white py-8 px-6 shadow-xl rounded-2xl">
        <form @submit.prevent="submit" class="space-y-6">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              <i class="fas fa-envelope mr-2 text-blue-600"></i>
              Correo electrónico
            </label>
            <input
              id="email"
              v-model.trim="email"
              type="email"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
              placeholder="tu@email.com"
            >
          </div>

          <!-- Nombre completo -->
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700 mb-2">
              <i class="fas fa-user mr-2 text-blue-600"></i>
              Nombre completo
            </label>
            <input
              id="full_name"
              v-model.trim="full_name"
              type="text"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
              placeholder="Tu nombre completo"
            >
          </div>

          <!-- Contraseña -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              <i class="fas fa-lock mr-2 text-blue-600"></i>
              Contraseña
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                placeholder="Mínimo 6 caracteres"
              >
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              La contraseña debe tener al menos 6 caracteres
            </p>
          </div>

          <!-- Confirmar contraseña -->
          <div>
            <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">
              <i class="fas fa-lock mr-2 text-blue-600"></i>
              Confirmar contraseña
            </label>
            <div class="relative">
              <input
                id="confirm_password"
                v-model="confirm_password"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                placeholder="Repite tu contraseña"
              >
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Términos y condiciones -->
          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="terms"
                v-model="acceptTerms"
                type="checkbox"
                required
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
            </div>
            <div class="ml-3 text-sm">
              <label for="terms" class="text-gray-700">
                Acepto los
                <a href="#" class="text-blue-600 hover:text-blue-500 font-medium">Términos de Servicio</a>
                y la
                <a href="#" class="text-blue-600 hover:text-blue-500 font-medium">Política de Privacidad</a>
              </label>
            </div>
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

          <!-- Success -->
          <div v-if="success" class="bg-green-50 border border-green-200 rounded-xl p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <i class="fas fa-check-circle text-green-400"></i>
              </div>
              <div class="ml-3">
                <p class="text-sm text-green-800">{{ success }}</p>
              </div>
            </div>
          </div>

          <!-- Botón de envío -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-orange-500 to-green-500 hover:from-orange-600 hover:to-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <span v-if="loading" class="flex items-center">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              Creando cuenta...
            </span>
            <span v-else class="flex items-center">
              <i class="fas fa-user-plus mr-2"></i>
              Crear Cuenta
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
              <span class="px-2 bg-white text-gray-500">¿Ya tienes cuenta?</span>
            </div>
          </div>
        </div>

        <!-- Link a login -->
        <div class="mt-6 text-center">
          <router-link
            to="/login"
            class="inline-flex items-center px-6 py-3 border border-gray-300 rounded-xl text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
          >
            <i class="fas fa-sign-in-alt mr-2"></i>
            Iniciar sesión
          </router-link>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center">
        <p class="text-xs text-gray-500">
          Al crear una cuenta, obtienes acceso a ofertas exclusivas y recomendaciones personalizadas
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Auth } from '../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

// Estado reactivo
const email = ref('')
const full_name = ref('')
const password = ref('')
const confirm_password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const acceptTerms = ref(false)

// Método de envío
async function submit() {
  error.value = ''
  success.value = ''
  
  // Validaciones
  if (!email.value || !password.value || !confirm_password.value) {
    error.value = 'Por favor completa todos los campos obligatorios'
    return
  }
  
  if (password.value.length < 6) {
    error.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }
  
  if (password.value !== confirm_password.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  
  if (!acceptTerms.value) {
    error.value = 'Debes aceptar los términos y condiciones'
    return
  }
  
  loading.value = true
  
  try {
    const { data } = await Auth.register({
      email: email.value,
      full_name: full_name.value || '',
      password: password.value
    })
    
    success.value = '¡Cuenta creada exitosamente! Te hemos enviado un email de confirmación.'
    
    // Limpiar formulario
    email.value = ''
    full_name.value = ''
    password.value = ''
    confirm_password.value = ''
    acceptTerms.value = false
    
    // Redirigir después de 2 segundos
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error al crear la cuenta. Intenta de nuevo.'
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
.hover\:from-orange-600:hover {
  --tw-gradient-from: #ea580c;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(234, 88, 12, 0));
}

.hover\:to-green-600:hover {
  --tw-gradient-to: #16a34a;
}
</style>
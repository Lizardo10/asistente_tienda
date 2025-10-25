<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar Profesional -->
    <nav class="bg-white shadow-lg border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex-shrink-0">
            <router-link to="/" class="flex items-center space-x-2">
              <div class="w-8 h-8 bg-gradient-to-r from-orange-500 to-green-500 rounded-lg flex items-center justify-center">
                <i class="fas fa-store text-white text-sm"></i>
              </div>
              <span class="text-xl font-bold text-gray-900">Asistente Tienda</span>
            </router-link>
          </div>

          <!-- Navegación Principal -->
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <router-link 
                to="/" 
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                active-class="text-blue-600 bg-blue-50"
              >
                <i class="fas fa-home mr-1"></i>Inicio
              </router-link>
              <router-link 
                to="/products" 
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                active-class="text-blue-600 bg-blue-50"
              >
                <i class="fas fa-shopping-bag mr-1"></i>Productos
              </router-link>
              
              <!-- Carrito para clientes -->
              <router-link 
                v-if="isLoggedIn && !isAdmin"
                to="/cart" 
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative"
                active-class="text-blue-600 bg-blue-50"
              >
                <i class="fas fa-shopping-cart mr-1"></i>Carrito
                <span v-if="cartCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {{ cartCount }}
                </span>
              </router-link>

              <!-- Pedidos para clientes -->
              <router-link 
                v-if="isLoggedIn && !isAdmin"
                to="/orders" 
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                active-class="text-blue-600 bg-blue-50"
              >
                <i class="fas fa-box mr-1"></i>Mis Pedidos
              </router-link>
            </div>
          </div>

          <!-- Lado Derecho -->
          <div class="flex items-center space-x-4">
            <!-- Admin Dropdown -->
            <div v-if="isAdmin" class="relative">
              <button 
                @click="toggleAdminMenu"
                class="flex items-center text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              >
                <i class="fas fa-cog mr-1"></i>
                Admin
                <i class="fas fa-chevron-down ml-1 text-xs"></i>
              </button>
              
              <!-- Admin Menu -->
              <div v-if="showAdminMenu" class="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                <div class="py-1">
                  <router-link to="/admin" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    <i class="fas fa-tachometer-alt mr-3 text-gray-400"></i>Dashboard
                  </router-link>
                  <router-link to="/admin/accounting" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    <i class="fas fa-calculator mr-3 text-gray-400"></i>Contabilidad
                  </router-link>
                  <router-link to="/admin/chat-history" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    <i class="fas fa-comments mr-3 text-gray-400"></i>Historial de Chat
                  </router-link>
                  <div class="border-t border-gray-100 my-1"></div>
                  <router-link to="/admin/products" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    <i class="fas fa-box mr-3 text-gray-400"></i>Gestionar Productos
                  </router-link>
                  <router-link to="/admin/orders" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    <i class="fas fa-shopping-bag mr-3 text-gray-400"></i>Gestionar Pedidos
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Usuario Autenticado -->
            <div v-if="isLoggedIn" class="flex items-center space-x-3">
              <div class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                  <i class="fas fa-user text-white text-xs"></i>
                </div>
                <span class="text-sm text-gray-700 font-medium">{{ session.user?.email }}</span>
                <span v-if="isAdmin" class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">
                  Admin
                </span>
              </div>
              <button 
                @click="logout" 
                class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
              >
                <i class="fas fa-sign-out-alt mr-1"></i>Salir
              </button>
            </div>

            <!-- Usuario No Autenticado -->
            <div v-else class="flex items-center space-x-3">
              <router-link 
                to="/login" 
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              >
                <i class="fas fa-sign-in-alt mr-1"></i>Iniciar Sesión
              </router-link>
              <router-link 
                to="/register" 
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
              >
                <i class="fas fa-user-plus mr-1"></i>Registrarse
              </router-link>
            </div>

            <!-- Mobile Menu Button -->
            <button 
              @click="toggleMobileMenu"
              class="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100"
            >
              <i class="fas fa-bars"></i>
            </button>
          </div>
        </div>

        <!-- Mobile Menu -->
        <div v-if="showMobileMenu" class="md:hidden">
          <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
            <router-link to="/" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
              <i class="fas fa-home mr-2"></i>Inicio
            </router-link>
            <router-link to="/products" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
              <i class="fas fa-shopping-bag mr-2"></i>Productos
            </router-link>
            <router-link v-if="isLoggedIn && !isAdmin" to="/cart" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
              <i class="fas fa-shopping-cart mr-2"></i>Carrito
            </router-link>
            <router-link v-if="isLoggedIn && !isAdmin" to="/orders" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
              <i class="fas fa-box mr-2"></i>Mis Pedidos
            </router-link>
            
            <!-- Admin links en mobile -->
            <div v-if="isAdmin" class="border-t border-gray-200 pt-2 mt-2">
              <router-link to="/admin" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
                <i class="fas fa-tachometer-alt mr-2"></i>Dashboard
              </router-link>
              <router-link to="/admin/accounting" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
                <i class="fas fa-calculator mr-2"></i>Contabilidad
              </router-link>
              <router-link to="/admin/chat-history" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
                <i class="fas fa-comments mr-2"></i>Historial de Chat
              </router-link>
              <router-link to="/admin/products" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
                <i class="fas fa-box mr-2"></i>Gestionar Productos
              </router-link>
              <router-link to="/admin/orders" class="block px-3 py-2 text-gray-700 hover:text-blue-600 rounded-md text-base font-medium">
                <i class="fas fa-shopping-bag mr-2"></i>Gestionar Pedidos
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Contenido Principal -->
    <main class="min-h-screen">
      <router-view />
    </main>

    <!-- Chat Flotante -->
    <FloatingChat />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { session, loadMe, setToken } from './services/session'
import { useRouter } from 'vue-router'
import FloatingChat from './components/FloatingChatPro.vue'

const router = useRouter()

// Estado reactivo
const cartCount = ref(0)
const showAdminMenu = ref(false)
const showMobileMenu = ref(false)

// cargar usuario al iniciar la app (si hay token)
onMounted(() => { 
  loadMe()
  loadCartCount()
})

const isLoggedIn = computed(() => !!session.token && !!session.user)
const isAdmin = computed(() => session.user?.role === 'admin')

function logout () {
  setToken(null)
  router.push('/login')
}

// Cargar cantidad de items en el carrito
async function loadCartCount() {
  try {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]')
    cartCount.value = cart.reduce((total, item) => total + item.quantity, 0)
  } catch (error) {
    console.error('Error cargando carrito:', error)
    cartCount.value = 0
  }
}

// Escuchar cambios en el carrito
window.addEventListener('storage', (e) => {
  if (e.key === 'cart') {
    loadCartCount()
  }
})

// Toggle admin menu
function toggleAdminMenu() {
  showAdminMenu.value = !showAdminMenu.value
}

// Toggle mobile menu
function toggleMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value
}

// Cerrar menús al hacer click fuera
document.addEventListener('click', (e) => {
  if (!e.target.closest('.relative')) {
    showAdminMenu.value = false
  }
})
</script>

<style scoped>
/* Estilos para el navbar profesional */
.router-link-active {
  color: #2563eb;
  background-color: #eff6ff;
}

/* Animaciones suaves */
.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}

/* Estilos para el dropdown */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
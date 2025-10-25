<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header de la página -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Nuestros Productos
          </h1>
          <p class="text-xl text-gray-600 mb-8">
            Descubre nuestra amplia selección de productos de calidad
          </p>
          
          <!-- Banner del Chat -->
          <div class="bg-gradient-to-r from-orange-50 to-green-50 rounded-2xl p-6 mb-8">
            <div class="flex flex-col sm:flex-row items-center justify-between">
              <div class="text-center sm:text-left mb-4 sm:mb-0">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">
                  <i class="fas fa-robot text-blue-600 mr-2"></i>
                  ¿Necesitas ayuda?
                </h3>
                <p class="text-gray-600">
                  Nuestro asistente IA está aquí para ayudarte con cualquier pregunta
                </p>
              </div>
              <router-link 
                to="/chat" 
                class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-green-500 text-white font-semibold rounded-xl hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300"
              >
                <i class="fas fa-comments mr-2"></i>
                Chatear con IA
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros y Búsqueda -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <div class="flex flex-col lg:flex-row gap-4">
          <!-- Búsqueda -->
          <div class="flex-1">
            <div class="relative">
              <input 
                v-model="searchQuery"
                type="text" 
                placeholder="Buscar productos..."
                class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
              <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            </div>
          </div>
          
          <!-- Filtro por categoría -->
          <div class="lg:w-64">
            <select 
              v-model="selectedCategory"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todas las categorías</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          
          <!-- Ordenar -->
          <div class="lg:w-48">
            <select 
              v-model="sortBy"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="title">Ordenar por nombre</option>
              <option value="price_asc">Precio: menor a mayor</option>
              <option value="price_desc">Precio: mayor a menor</option>
              <option value="stock">Stock disponible</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Recomendaciones -->
      <div v-if="recommendations.length > 0" class="mb-8">
        <div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-6">
          <div class="flex items-center mb-4">
            <i class="fas fa-star text-yellow-500 text-2xl mr-3"></i>
            <h3 class="text-xl font-bold text-gray-900">
              {{ recommendationMessage }}
            </h3>
          </div>
          
          <div v-if="userInfo.is_client && userInfo.has_history" class="mb-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
              <i class="fas fa-shopping-bag mr-1"></i>
              Cliente con {{ userInfo.total_orders }} compra{{ userInfo.total_orders !== 1 ? 's' : '' }} anterior{{ userInfo.total_orders !== 1 ? 'es' : '' }}
            </span>
          </div>
          <div v-else-if="userInfo.is_client" class="mb-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
              <i class="fas fa-user-plus mr-1"></i>
              ¡Bienvenido! Productos destacados para ti
            </span>
          </div>
          <div v-else class="mb-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800">
              <i class="fas fa-gift mr-1"></i>
              Productos populares - 
              <router-link to="/login" class="ml-1 underline">Inicia sesión</router-link> 
              para recomendaciones personalizadas
            </span>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div 
              v-for="product in recommendations" 
              :key="product.id"
              class="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden"
            >
              <div class="relative">
                <img 
                  :src="resolveImage(product.image_url)" 
                  :alt="product.title"
                  class="w-full h-48 object-cover"
                >
                <div class="absolute top-3 right-3 bg-yellow-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                  ⭐ Recomendado
                </div>
              </div>
              <div class="p-4">
                <h4 class="font-semibold text-gray-900 mb-2">{{ product.title }}</h4>
                <p class="text-gray-600 text-sm mb-3">{{ product.description }}</p>
                <div class="flex items-center justify-between mb-3">
                  <span class="text-lg font-bold text-blue-600">Q{{ product.price.toFixed(2) }}</span>
                  <span class="text-sm text-gray-500">Stock: {{ product.stock }}</span>
                </div>
                <button 
                  @click="addToCart(product)"
                  class="w-full bg-gradient-to-r from-orange-500 to-green-500 text-white py-2 rounded-lg font-medium hover:shadow-lg transition-all duration-300"
                >
                  <i class="fas fa-cart-plus mr-1"></i>
                  Agregar al Carrito
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Lista de productos -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900">
            Todos los Productos
            <span class="text-lg font-normal text-gray-500">({{ filteredProducts.length }})</span>
          </h2>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div 
            v-for="product in paginatedProducts" 
            :key="product.id"
            class="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden"
          >
            <div class="relative">
              <img 
                :src="resolveImage(product.image_url)" 
                :alt="product.title"
                class="w-full h-48 object-cover"
              >
              <div class="absolute top-3 right-3 bg-blue-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                {{ product.category }}
              </div>
              <div v-if="product.stock === 0" class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <span class="bg-red-500 text-white px-3 py-1 rounded-full font-bold">Sin Stock</span>
              </div>
            </div>
            <div class="p-4">
              <h4 class="font-semibold text-gray-900 mb-2">{{ product.title }}</h4>
              <p class="text-gray-600 text-sm mb-3">{{ product.description }}</p>
              <div class="flex items-center justify-between mb-3">
                <span class="text-lg font-bold text-blue-600">Q{{ product.price.toFixed(2) }}</span>
                <span 
                  class="text-sm px-2 py-1 rounded-full"
                  :class="product.stock > 10 ? 'bg-green-100 text-green-800' : product.stock > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'"
                >
                  {{ product.stock > 0 ? `${product.stock} disponibles` : 'Sin existencia' }}
                </span>
              </div>
              <button 
                @click="addToCart(product)"
                :disabled="product.stock === 0"
                class="w-full py-2 rounded-lg font-medium transition-all duration-300"
                :class="product.stock > 0 
                  ? 'bg-gradient-to-r from-orange-500 to-green-500 text-white hover:shadow-lg' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'"
              >
                <i class="fas fa-cart-plus mr-1"></i>
                {{ product.stock > 0 ? 'Agregar al Carrito' : 'Sin Stock' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Paginación -->
        <div v-if="totalPages > 1" class="flex justify-center mt-8">
          <nav class="flex space-x-2">
            <button 
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="currentPage = page"
              class="px-3 py-2 rounded-lg border"
              :class="page === currentPage 
                ? 'bg-blue-600 text-white border-blue-600' 
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'"
            >
              {{ page }}
            </button>
            
            <button 
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'
import { session } from '../services/session'

// Estado reactivo
const products = ref([])
const recommendations = ref([])
const userInfo = ref({})
const recommendationMessage = ref('')
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('title')
const currentPage = ref(1)
const itemsPerPage = 12

// Computed properties
const categories = computed(() => {
  const cats = [...new Set(products.value.map(p => p.category))]
  return cats.sort()
})

const filteredProducts = computed(() => {
  let filtered = products.value

  // Filtrar por búsqueda
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.title.toLowerCase().includes(query) || 
      p.description.toLowerCase().includes(query)
    )
  }

  // Filtrar por categoría
  if (selectedCategory.value) {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }

  // Ordenar
  switch (sortBy.value) {
    case 'price_asc':
      filtered = filtered.sort((a, b) => a.price - b.price)
      break
    case 'price_desc':
      filtered = filtered.sort((a, b) => b.price - a.price)
      break
    case 'stock':
      filtered = filtered.sort((a, b) => b.stock - a.stock)
      break
    default:
      filtered = filtered.sort((a, b) => a.title.localeCompare(b.title))
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredProducts.value.length / itemsPerPage)
})

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredProducts.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Métodos
async function loadProducts() {
  try {
    const response = await api.get('/products')
    products.value = response.data
  } catch (error) {
    console.error('Error cargando productos:', error)
  }
}

async function loadRecommendations() {
  try {
    const response = await api.get('/recommendations/for-you')
    recommendations.value = response.data.recommendations || []
    userInfo.value = response.data.user_info || {}
    recommendationMessage.value = response.data.message || 'Productos recomendados para ti'
  } catch (error) {
    console.error('Error cargando recomendaciones:', error)
  }
}

function resolveImage(imageUrl) {
  if (!imageUrl) {
    return 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=500&h=300&fit=crop'
  }
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  return `http://localhost:8000${imageUrl}`
}

function addToCart(product) {
  if (product.stock === 0) return
  
  try {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]')
    const existingItem = cart.find(item => item.id === product.id)
    
    if (existingItem) {
      existingItem.quantity += 1
    } else {
      cart.push({
        id: product.id,
        title: product.title,
        price: product.price,
        image_url: product.image_url,
        quantity: 1
      })
    }
    
    localStorage.setItem('cart', JSON.stringify(cart))
    
    // Mostrar notificación
    alert(`¡${product.title} agregado al carrito!`)
    
    // Actualizar contador del navbar
    window.dispatchEvent(new Event('storage'))
  } catch (error) {
    console.error('Error agregando al carrito:', error)
  }
}

// Watchers
watch([searchQuery, selectedCategory, sortBy], () => {
  currentPage.value = 1
})

// Cargar datos al montar
onMounted(() => {
  loadProducts()
  loadRecommendations()
})
</script>

<style scoped>
/* Animaciones suaves */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* Efectos hover */
.hover\:-translate-y-1:hover {
  transform: translateY(-0.25rem);
}

.hover\:-translate-y-2:hover {
  transform: translateY(-0.5rem);
}

/* Gradientes personalizados */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}
</style>
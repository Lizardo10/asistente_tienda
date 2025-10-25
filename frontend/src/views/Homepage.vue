<template>
  <div class="min-h-screen bg-white">
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-br from-orange-50 via-white to-green-50 py-20">
      <div class="absolute inset-0 bg-gradient-to-r from-orange-500/5 to-green-500/5"></div>
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <!-- Badge -->
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-8">
            <i class="fas fa-star text-yellow-500 mr-2"></i>
            Tienda #1 en Guatemala
          </div>
          
          <!-- Título Principal -->
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Moda que
            <span class="bg-gradient-to-r from-orange-500 to-green-500 bg-clip-text text-transparent">
              te define
            </span>
          </h1>
          
          <!-- Subtítulo -->
          <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Descubre las últimas tendencias en ropa, calzado y accesorios. 
            Calidad premium, precios increíbles y envío gratis a todo el país.
          </p>
          
          <!-- Botones de Acción -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <router-link 
              to="/products" 
              class="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-orange-500 to-green-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
            >
              <i class="fas fa-shopping-bag mr-2"></i>
              Explorar Productos
            </router-link>
            <router-link 
              to="/chat" 
              class="inline-flex items-center justify-center px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-300"
            >
              <i class="fas fa-robot mr-2"></i>
              Asistente IA
            </router-link>
          </div>
          
          <!-- Características -->
          <div class="flex flex-wrap justify-center gap-8 text-sm text-gray-600">
            <div class="flex items-center">
              <i class="fas fa-shipping-fast text-green-500 mr-2"></i>
              Envío Gratis
            </div>
            <div class="flex items-center">
              <i class="fab fa-paypal text-blue-500 mr-2"></i>
              Pagos Seguros
            </div>
            <div class="flex items-center">
              <i class="fas fa-undo text-purple-500 mr-2"></i>
              30 Días Devolución
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Productos Destacados -->
    <section class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Productos Destacados
          </h2>
          <p class="text-xl text-gray-600">
            Los productos más populares de nuestra tienda
          </p>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          <div 
            v-for="product in featuredProducts" 
            :key="product.id"
            class="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden"
          >
            <div class="relative">
              <img 
                :src="resolveImage(product.image_url)" 
                :alt="product.title"
                class="w-full h-64 object-cover"
              >
              <div class="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                Destacado
              </div>
            </div>
            <div class="p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ product.title }}</h3>
              <p class="text-gray-600 text-sm mb-4">{{ product.description }}</p>
              <div class="flex items-center justify-between">
                <span class="text-2xl font-bold text-blue-600">Q{{ product.price.toFixed(2) }}</span>
                <span class="text-sm text-gray-500">Stock: {{ product.stock }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="text-center mt-12">
          <router-link 
            to="/products" 
            class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-orange-500 to-green-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
          >
            Ver Todos los Productos
            <i class="fas fa-arrow-right ml-2"></i>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Estadísticas -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
          <div class="space-y-2">
            <div class="text-4xl sm:text-5xl font-bold text-blue-600">500+</div>
            <div class="text-lg font-semibold text-gray-600">Productos</div>
          </div>
          <div class="space-y-2">
            <div class="text-4xl sm:text-5xl font-bold text-purple-600">1000+</div>
            <div class="text-lg font-semibold text-gray-600">Clientes</div>
          </div>
          <div class="space-y-2">
            <div class="text-4xl sm:text-5xl font-bold text-green-600">4.9★</div>
            <div class="text-lg font-semibold text-gray-600">Calificación</div>
          </div>
          <div class="space-y-2">
            <div class="text-4xl sm:text-5xl font-bold text-orange-600">24/7</div>
            <div class="text-lg font-semibold text-gray-600">Soporte</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Características -->
    <section class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            ¿Por qué elegirnos?
          </h2>
          <p class="text-xl text-gray-600">
            Ofrecemos la mejor experiencia de compra online
          </p>
        </div>
        
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
            <div class="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mb-6">
              <i class="fas fa-shipping-fast text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">Envío Gratis</h3>
            <p class="text-gray-600 leading-relaxed">
              Envío gratuito en compras superiores a Q200. Entrega rápida y segura a todo Guatemala.
            </p>
          </div>
          
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6">
              <i class="fab fa-paypal text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">Pago Seguro</h3>
            <p class="text-gray-600 leading-relaxed">
              Pagos 100% seguros con PayPal. Protección total de tus datos y transacciones.
            </p>
          </div>
          
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6">
              <i class="fas fa-undo text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">Devoluciones</h3>
            <p class="text-gray-600 leading-relaxed">
              30 días para devoluciones. Proceso fácil y sin complicaciones.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Sección IA -->
    <section class="py-20 bg-gradient-to-r from-orange-500 to-green-500">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="text-white">
          <h2 class="text-3xl sm:text-4xl font-bold mb-6">
            Asistente de Compra con IA
          </h2>
          <p class="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Nuestro asistente inteligente te ayuda a encontrar exactamente lo que buscas. 
            Búsqueda por voz, recomendaciones personalizadas y soporte 24/7.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/chat" 
              class="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
            >
              <i class="fas fa-comments mr-2"></i>
              Probar Asistente IA
            </router-link>
            <router-link 
              to="/products" 
              class="inline-flex items-center justify-center px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-blue-600 transition-all duration-300"
            >
              <i class="fas fa-search mr-2"></i>
              Buscar Productos
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Newsletter -->
    <section class="py-20 bg-white">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
          Mantente al día
        </h2>
        <p class="text-xl text-gray-600 mb-8">
          Recibe ofertas exclusivas y las últimas novedades en tu correo
        </p>
        <div class="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
          <input 
            type="email" 
            placeholder="Tu correo electrónico"
            class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
          <button class="px-8 py-3 bg-gradient-to-r from-orange-500 to-green-500 text-white font-semibold rounded-lg hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300">
            Suscribirse
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

// Estado reactivo
const featuredProducts = ref([])

// Cargar productos destacados
async function loadFeaturedProducts() {
  try {
    const response = await api.get('/products')
    // Tomar los primeros 8 productos como destacados
    featuredProducts.value = response.data.slice(0, 8)
  } catch (error) {
    console.error('Error cargando productos destacados:', error)
  }
}

// Resolver imagen
function resolveImage(imageUrl) {
  if (!imageUrl) {
    return 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=500&h=300&fit=crop'
  }
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  return `http://localhost:8000${imageUrl}`
}

// Cargar datos al montar
onMounted(() => {
  loadFeaturedProducts()
})
</script>

<style scoped>
/* Animaciones suaves */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* Gradientes personalizados */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

/* Efectos hover */
.hover\:-translate-y-1:hover {
  transform: translateY(-0.25rem);
}

.hover\:-translate-y-2:hover {
  transform: translateY(-0.5rem);
}
</style>
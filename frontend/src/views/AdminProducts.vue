<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Gestión de Productos</h1>
            <p class="mt-2 text-gray-600">Administra el catálogo de productos de la tienda</p>
          </div>
          <button 
            @click="showAddModal = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200"
          >
            <i class="fas fa-plus mr-2"></i>
            Agregar Producto
          </button>
        </div>
      </div>
    </div>

    <!-- Estadísticas -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-blue-100 rounded-lg">
              <i class="fas fa-box text-blue-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Productos</p>
              <p class="text-2xl font-bold text-gray-900">{{ products.length }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-green-100 rounded-lg">
              <i class="fas fa-check-circle text-green-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">En Stock</p>
              <p class="text-2xl font-bold text-gray-900">{{ productsInStock }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-red-100 rounded-lg">
              <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Sin Stock</p>
              <p class="text-2xl font-bold text-gray-900">{{ productsOutOfStock }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg">
          <div class="flex items-center">
            <div class="p-3 bg-purple-100 rounded-lg">
              <i class="fas fa-tags text-purple-600 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Categorías</p>
              <p class="text-2xl font-bold text-gray-900">{{ categories.length }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div class="flex flex-col lg:flex-row gap-4">
          <div class="flex-1">
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Buscar productos..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
          </div>
          <div class="lg:w-64">
            <select 
              v-model="selectedCategory"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todas las categorías</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          <div class="lg:w-48">
            <select 
              v-model="stockFilter"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos</option>
              <option value="in_stock">En Stock</option>
              <option value="out_of_stock">Sin Stock</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Tabla de productos -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Producto
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Categoría
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="product in filteredProducts" :key="product.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-12 w-12">
                      <img 
                        :src="resolveImage(product.image_url)" 
                        :alt="product.title"
                        class="h-12 w-12 rounded-lg object-cover"
                      >
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ product.title }}</div>
                      <div class="text-sm text-gray-500">{{ product.description }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ product.category }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  Q{{ product.price.toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ product.stock }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="product.stock > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ product.stock > 0 ? 'Disponible' : 'Sin Stock' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button 
                      @click="editProduct(product)"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button 
                      @click="deleteProduct(product.id)"
                      class="text-red-600 hover:text-red-900"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal para agregar/editar producto -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ showAddModal ? 'Agregar Producto' : 'Editar Producto' }}
          </h3>
          
          <form @submit.prevent="saveProduct" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Título</label>
              <input 
                v-model="productForm.title"
                type="text" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Descripción</label>
              <textarea 
                v-model="productForm.description"
                required
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Precio</label>
              <input 
                v-model="productForm.price"
                type="number" 
                step="0.01"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Stock</label>
              <input 
                v-model="productForm.stock"
                type="number" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Categoría</label>
              <input 
                v-model="productForm.category"
                type="text" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">URL de Imagen</label>
              <input 
                v-model="productForm.image_url"
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button 
                type="button"
                @click="closeModal"
                class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button 
                type="submit"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {{ showAddModal ? 'Agregar' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

// Estado reactivo
const products = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const stockFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const productForm = ref({
  title: '',
  description: '',
  price: 0,
  stock: 0,
  category: '',
  image_url: ''
})

// Computed properties
const categories = computed(() => {
  const cats = [...new Set(products.value.map(p => p.category))]
  return cats.sort()
})

const productsInStock = computed(() => {
  return products.value.filter(p => p.stock > 0).length
})

const productsOutOfStock = computed(() => {
  return products.value.filter(p => p.stock === 0).length
})

const filteredProducts = computed(() => {
  let filtered = products.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.title.toLowerCase().includes(query) || 
      p.description.toLowerCase().includes(query)
    )
  }

  if (selectedCategory.value) {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }

  if (stockFilter.value === 'in_stock') {
    filtered = filtered.filter(p => p.stock > 0)
  } else if (stockFilter.value === 'out_of_stock') {
    filtered = filtered.filter(p => p.stock === 0)
  }

  return filtered
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

function resolveImage(imageUrl) {
  if (!imageUrl) {
    return 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&h=100&fit=crop'
  }
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  return `http://localhost:8000${imageUrl}`
}

function editProduct(product) {
  productForm.value = { ...product }
  showEditModal.value = true
}

async function deleteProduct(productId) {
  if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
    try {
      await api.delete(`/products/${productId}`)
      await loadProducts()
    } catch (error) {
      console.error('Error eliminando producto:', error)
    }
  }
}

async function saveProduct() {
  try {
    if (showAddModal.value) {
      await api.post('/products', productForm.value)
    } else {
      await api.put(`/products/${productForm.value.id}`, productForm.value)
    }
    
    await loadProducts()
    closeModal()
  } catch (error) {
    console.error('Error guardando producto:', error)
  }
}

function closeModal() {
  showAddModal.value = false
  showEditModal.value = false
  productForm.value = {
    title: '',
    description: '',
    price: 0,
    stock: 0,
    category: '',
    image_url: ''
  }
}

// Cargar datos al montar
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
/* Animaciones suaves */
.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}
</style>












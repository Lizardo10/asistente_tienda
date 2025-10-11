<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h3 class="mb-0">Panel de administración</h3>
    </div>

    <!-- Tabs de navegación -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button 
          :class="['nav-link', { active: activeTab === 'products' }]" 
          @click="activeTab = 'products'"
        >
          Productos
        </button>
      </li>
      <li class="nav-item">
        <button 
          :class="['nav-link', { active: activeTab === 'orders' }]" 
          @click="activeTab = 'orders'"
        >
          Historial de Compras
        </button>
      </li>
    </ul>

    <!-- Contenido de Productos -->
    <div v-if="activeTab === 'products'">

    
    <div v-if="editing" class="card mb-4 border-primary">
      <div class="card-body">
        <h5 class="card-title mb-3">Editar producto</h5>
        <ProductForm :value="editModel" mode="edit" @submit="updateProduct" @cancel="cancelEdit" />
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3">Crear producto</h5>
        <form @submit.prevent="createProduct" class="row g-3">
          <div class="col-md-6">
            <label class="form-label">Título</label>
            <input v-model.trim="form.title" class="form-control" required />
          </div>
          <div class="col-md-3">
            <label class="form-label">Precio</label>
            <input v-model.number="form.price" type="number" min="0" step="0.01" class="form-control" required />
          </div>
          <div class="col-md-12">
            <label class="form-label">Descripción</label>
            <textarea v-model.trim="form.description" class="form-control" rows="3"></textarea>
          </div>
          <div class="col-md-6">
            <label class="form-label">Imagen principal (URL opcional)</label>
            <input v-model.trim="form.image_url" class="form-control" placeholder="http://..." />
          </div>
          <div class="col-md-6">
            <label class="form-label">Subir imagen (archivo)</label>
            <input ref="fileRef" type="file" accept="image/*" class="form-control" />
          </div>
          <div class="col-12">
            <button class="btn btn-primary" :disabled="loading">Guardar</button>
          </div>
          <div class="text-danger" v-if="error">{{ error }}</div>
          <div class="text-success" v-if="ok">¡Producto creado!</div>
        </form>
      </div>
    </div>

    <h5 class="mb-2">Productos</h5>
    <div class="row g-3">
      <div v-for="p in products" :key="p.id" class="col-12 col-sm-6 col-md-4 col-lg-3">
        <div class="card h-100 shadow-sm">
          <img :src="resolveImage(p.image_url || (p.images?.[0]?.url ?? ''))" class="card-img-top" alt="producto">
          <div class="card-body d-flex flex-column">
            <h6 class="card-title">{{ p.title }}</h6>
            <p class="card-text small text-muted flex-grow-1">{{ p.description }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <span class="fw-semibold">Q {{ p.price.toFixed(2) }}</span>
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" @click="startEdit(p)">Editar</button>
                <button class="btn btn-outline-danger" @click="remove(p.id)" :disabled="loading">Eliminar</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <p v-if="products.length === 0" class="text-muted">Aún no hay productos</p>
    </div>
    </div>

    <!-- Contenido de Órdenes -->
    <div v-if="activeTab === 'orders'">
      <AdminOrders />
    </div>
  </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
import DOMPurify from 'dompurify'
import { Products } from '../services/api'
import api from '../services/api'
const PLACEHOLDER_IMG = 'https://via.placeholder.com/600x400?text=Producto'
import ProductForm from '../components/ProductForm.vue'
import AdminOrders from '../components/AdminOrders.vue'

const activeTab = ref('products') // 'products' o 'orders'

const form = ref({ title: '', price: 0, description: '', image_url: '' })
const products = ref([])
const loading = ref(false)
const error = ref('')
const ok = ref(false)
const fileRef = ref(null)
function resolveImage(u) {
  if (!u) return PLACEHOLDER_IMG
  if (!/^https?:\/\//i.test(u)) {
    const base = (api?.defaults?.baseURL || '').replace(/\/$/, '')
    return base + u
  }
  return u
}


const editing = ref(false)
const editModel = ref(null)

function startEdit(p) {
  // clonar datos mínimos
  editModel.value = {
    id: p.id,
    title: p.title ?? '',
    price: Number(p.price ?? 0),
    description: p.description ?? '',
    image_url: p.image_url ?? (p.images?.[0]?.url ?? ''),
    active: typeof p.active === 'boolean' ? p.active : true
  }
  editing.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
  editing.value = false
  editModel.value = null
}

async function updateProduct(payload) {
  if (!editModel.value?.id) return
  loading.value = true
  try {
    const sanitized = {
      title: sanitize(payload.title),
      description: sanitize(payload.description),
      price: Number(payload.price),
      image_url: sanitize(payload.image_url),
      active: payload.active
    }
    await api.put(`/products/${editModel.value.id}`, sanitized)
    await load()
    ok.value = true
    setTimeout(() => ok.value = false, 2000)
    cancelEdit()
  } catch (e) {
    alert(e?.response?.data?.detail || 'Error actualizando')
  } finally {
    loading.value = false
  }
}


function sanitize(s){ return DOMPurify.sanitize(s ?? '') }

async function load() {
  const { data } = await Products.list()
  products.value = data
}

function logout() {
  localStorage.removeItem('token')
  location.href = '/login'
}

async function createProduct() {
  error.value = ''; ok.value = false
  if (!form.value.title || !form.value.price) {
    error.value = 'Completa título y precio'
    return
  }
  loading.value = true
  try {
    // 1) crear producto
    const payload = {
      title: sanitize(form.value.title),
      description: sanitize(form.value.description),
      price: Number(form.value.price),
      image_url: sanitize(form.value.image_url),
    }
    const { data: prod } = await Products.create(payload)

    // 2) si hay archivo, subirlo
    const file = fileRef.value?.files?.[0]
    if (file) {
      await Products.uploadImage(prod.id, file)
    }

    // 3) limpiar y recargar
    form.value = { title: '', price: 0, description: '', image_url: '' }
    if (fileRef.value) fileRef.value.value = ''
    ok.value = true
    await load()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error creando producto'
  } finally {
    loading.value = false
  }
}

async function remove(id) {
  if (!confirm('¿Eliminar producto?')) return
  loading.value = true
  try {
    await Products.remove(id)
    await load()
  } catch (e) {
    alert(e?.response?.data?.detail || 'Error eliminando')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

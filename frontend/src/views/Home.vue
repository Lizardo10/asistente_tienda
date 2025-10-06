<template>
  <div>
    <h2 class="mb-3">Productos</h2>
    <div class="row g-3">
      <div v-for="p in products" :key="p.id" class="col-12 col-sm-6 col-md-4 col-lg-3">
        <div class="card h-100 shadow-sm">
          <img :src="resolveImage(p.image_url || (p.images?.[0]?.url ?? ''))" class="card-img-top" alt="producto">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">{{ p.title }}</h5>
            <p class="card-text small text-muted flex-grow-1">{{ p.description }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <span class="fw-semibold">Q {{ p.price.toFixed(2) }}</span>
              <div v-if="isClient" class="d-flex align-items-center" style="gap:.5rem;">
  <input type="number" min="1" v-model.number="qty[p.id]" class="form-control form-control-sm" style="width:80px" placeholder="1">
  <button class="btn btn-sm btn-outline-primary" @click="addToCart(p)">Agregar</button>
</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { Products } from '../services/api'
import { session, loadMe } from '../services/session'
const PLACEHOLDER_IMG = 'https://via.placeholder.com/600x400?text=Producto'
const products = ref([])

function resolveImage(u) {
  if (!u) return PLACEHOLDER_IMG
  if (!/^https?:\/\//i.test(u)) {
    const base = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/$/, '')
    return base + u
  }
  return u
}

const qty = reactive({})
const isClient = computed(() => !!session.user && !session.user.is_admin) // cantidades por producto
async function load() { const { data } = await Products.list(); products.value = data }
import { add as addToCartAction } from '../services/cart'
function addToCart(p) {
  if (!qty[p.id] || qty[p.id] < 1) qty[p.id] = 1
  const amount = qty[p.id]
  addToCartAction(p, amount)
  alert(`Agregado al carrito: ${p.title} x ${amount}`)
}
onMounted(async () => { if (session.token && !session.user) await loadMe(); await load() })
</script>

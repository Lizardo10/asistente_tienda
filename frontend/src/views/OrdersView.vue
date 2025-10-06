<template>
  <div>
    <h3 class="mb-3">Mis pedidos</h3>

    <div v-if="loading" class="alert alert-info">Cargando...</div>
    <div v-else-if="!orders.length" class="alert alert-warning">Aún no tienes pedidos.</div>

    <div v-else class="vstack gap-3">
      <div class="card" v-for="o in orders" :key="o.id">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
              <div class="fw-semibold">Pedido #{{ o.code || o.id }}</div>
              <div class="text-muted small">{{ formatDate(o.created_at) }}</div>
            </div>
            <div class="fw-bold">Q {{ Number(o.total || sum(o.items)).toFixed(2) }}</div>
          </div>

          <ul class="list-group">
            <li class="list-group-item d-flex align-items-center justify-content-between"
                v-for="it in o.items" :key="it.product_id + '-' + it.quantity">
              <div class="d-flex align-items-center" style="gap:.75rem;">
                <img :src="resolveImage(productImage(it.product_id))" alt=""
                     style="width:48px;height:48px;object-fit:cover;border-radius:.25rem;" />
                <div>
                  <div class="fw-semibold">{{ productTitle(it.product_id) }}</div>
                  <div class="text-muted small">
                    Q {{ Number(it.price_each).toFixed(2) }} x {{ it.quantity }}
                  </div>
                </div>
              </div>
              <div>Q {{ (Number(it.price_each) * Number(it.quantity)).toFixed(2) }}</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Orders, Products } from '../services/api'
import { session, loadMe } from '../services/session'

const orders = ref([])
const loading = ref(true)
const products = ref([])

const PLACEHOLDER_IMG = 'https://via.placeholder.com/600x400?text=Producto'
function resolveImage(u) {
  if (!u) return PLACEHOLDER_IMG
  if (!/^https?:\/\//i.test(u)) {
    const base = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/$/, '')
    return base + u
  }
  return u
}

function productById(id) { return products.value.find(p => p.id === id) }
function productTitle(id) { return productById(id)?.title || `Producto ${id}` }
function productImage(id) {
  const p = productById(id)
  return p?.image_url || p?.images?.[0]?.url || ''
}
function sum(items) {
  return (items || []).reduce((a,b) => a + Number(b.price_each||0) * Number(b.quantity||1), 0)
}
function formatDate(iso) { try { return new Date(iso).toLocaleString() } catch { return iso || '' } }

onMounted(async () => {
  if (session.token && !session.user) await loadMe()
  // catálogo para miniaturas/títulos
  const { data: prods } = await Products.list()
  products.value = Array.isArray(prods) ? prods : []
  // pedidos del cliente
  const { data } = await Orders.my()
  orders.value = Array.isArray(data) ? data : (data?.results || [])
  loading.value = false
})
</script>

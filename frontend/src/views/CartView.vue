<template>
  <div>
    <h3 class="mb-3">Tu carrito</h3>

    <div v-if="!cart.items.length" class="alert alert-info">Tu carrito está vacío.</div>

    <div v-else class="row g-3">
      <div class="col-12 col-lg-8">
        <ul class="list-group">
  <li
    class="list-group-item d-flex align-items-center justify-content-between"
    v-for="it in cart.items"
    :key="it.id">
    <div class="d-flex align-items-center" style="gap:.75rem;">
      <img
        :src="resolveImage(it.image_url || it.images?.[0]?.url)"
        alt=""
        style="width:64px;height:64px;object-fit:cover;border-radius:.25rem;" />
      <div>
        <div class="fw-semibold">{{ it.title }}</div>
        <div class="text-muted small">Q {{ it.price.toFixed(2) }}</div>
      </div>
    </div>
    <div class="d-flex align-items-center" style="gap:.5rem;">
      <input type="number" min="1" v-model.number="it.quantity"
             class="form-control form-control-sm" style="width:80px" />
      <button class="btn btn-sm btn-outline-danger" @click="remove(it.id)">Quitar</button>
    </div>
  </li>
</ul>

      </div>

      <div class="col-12 col-lg-4">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
              <span>Items</span>
              <span>{{ count }}</span>
            </div>
            <div class="d-flex justify-content-between mb-3">
              <strong>Total</strong>
              <strong>Q {{ total.toFixed(2) }}</strong>
            </div>
            <button class="btn btn-primary w-100" :disabled="!cart.items.length" @click="checkout">Finalizar compra</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { cart, count, total, clear, remove, toOrderPayload } from '../services/cart'
import { Orders } from '../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const PLACEHOLDER_IMG = 'https://via.placeholder.com/600x400?text=Producto'
function resolveImage(u) {
  if (!u) return PLACEHOLDER_IMG
  if (!/^https?:\/\//i.test(u)) {
    const base = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/$/, '')
    return base + u
  }
  return u
}

async function checkout() {
  try {
    const payload = toOrderPayload()       
    await Orders.create(payload)            // ⬅️ POST /orders
    clear()
    alert('¡Compra realizada con éxito!')
    router.push('/orders')
  } catch (e) {
    // Deja esto para ver el motivo real si vuelve a fallar
    console.error('checkout error:', e)
    alert(e?.response?.data?.detail || 'Error al procesar la compra')
  }
}
</script>

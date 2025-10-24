import { reactive, computed, watch } from 'vue'

const saved = JSON.parse(localStorage.getItem('cart') || '[]')

export const cart = reactive({
  items: saved // [{id,title,price,image_url,quantity}]
})

export const count = computed(() => cart.items.reduce((a,b) => a + (b.quantity||0), 0))
export const total = computed(() => cart.items.reduce((a,b) => a + Number(b.price||0) * Number(b.quantity||1), 0))

watch(() => cart.items, (v) => {
  localStorage.setItem('cart', JSON.stringify(v))
}, { deep: true })

export function add(product, qty = 1) {
  const id = product.id
  const existing = cart.items.find(it => it.id === id)
  if (existing) existing.quantity += qty
  else cart.items.push({ id, title: product.title, price: product.price, image_url: product.image_url || (product.images?.[0]?.url ?? ''), quantity: qty })
}

export function remove(id) {
  const idx = cart.items.findIndex(it => it.id === id)
  if (idx !== -1) cart.items.splice(idx, 1)
}

export function clear() {
  cart.items.splice(0, cart.items.length)
}

export function updateQuantity(id, newQuantity) {
  const item = cart.items.find(it => it.id === id)
  if (item) {
    item.quantity = Math.max(1, newQuantity)
  }
}

export function toOrderPayload () {
  return {
    items: cart.items.map(it => ({
      product_id: it.id,
      quantity: Number(it.quantity || 1)
      // el backend toma el precio actual del producto
    }))
  }
}

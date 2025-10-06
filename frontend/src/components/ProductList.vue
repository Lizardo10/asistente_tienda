<template>
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap:1rem;">
    <div v-for="p in products" :key="p.id" style="border:1px solid #ddd; padding: .75rem; border-radius:.5rem;">
      <img v-if="p.image_url" :src="p.image_url" alt="" style="width:100%; height:140px; object-fit:cover; border-radius:.25rem;" />
      <h3 style="margin:.5rem 0;">{{ p.title }}</h3>
      <p style="font-size:.9rem; color:#555;">{{ p.description }}</p>
      <strong>Q {{ p.price.toFixed(2) }}</strong>
      <div style="margin-top:.5rem;">
        <button @click="$emit('add', p)">Agregar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const products = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/products')
    products.value = data
  } catch (e) {
    console.error(e)
  }
})
</script>

<template>
  <aside>
    <h3>Carrito ({{ count }})</h3>
    <ul>
      <li v-for="it in cart.items" :key="it.id">{{ it.title }} x {{ it.quantity }}</li>
    </ul>
    <button @click="$router.push('/cart')" :disabled="!cart.items.length">Ir al carrito</button>
  </aside>
</template>

<script setup>
import { cart, count } from '../services/cart'
</script>

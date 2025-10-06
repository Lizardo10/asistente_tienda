<template>
  <div class="mx-auto" style="max-width:420px">
    <h3 class="mb-3">Iniciar sesión</h3>
    <form @submit.prevent="submit" novalidate>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model.trim="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Contraseña</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <button class="btn btn-primary" :disabled="loading">Entrar</button>
      <a class="btn btn-link" href="/reset-password">¿Olvidaste tu contraseña?</a>
      <div class="text-danger mt-2" v-if="error">{{ error }}</div>
    </form>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Auth } from '../services/api'
const email = ref(''); const password = ref('')
const loading = ref(false); const error = ref('')
async function submit() {
  error.value = ''
  if (!email.value || !password.value) { error.value = 'Completa email y contraseña'; return }
  loading.value = true
  try {
    const { data } = await Auth.login({ email: email.value, password: password.value })
    localStorage.setItem('token', data.access_token)
    location.href = '/'
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error al iniciar sesión'
  } finally { loading.value = false }
}
</script>

<template>
  <div class="mx-auto" style="max-width:480px">
    <h3 class="mb-3">Crear cuenta</h3>
    <form @submit.prevent="submit" novalidate>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model.trim="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Nombre</label>
        <input v-model.trim="full_name" type="text" class="form-control" />
      </div>
      <div class="mb-3">
        <label class="form-label">Contraseña</label>
        <input v-model="password" type="password" class="form-control" minlength="6" required />
      </div>
      <button class="btn btn-primary" :disabled="loading">Registrarme</button>
      <div class="text-danger mt-2" v-if="error">{{ error }}</div>
    </form>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Auth } from '../services/api'
import DOMPurify from 'dompurify'
const email = ref(''); const full_name = ref(''); const password = ref('')
const loading = ref(false); const error = ref('')
async function submit() {
  error.value = ''
  if (!email.value || !password.value) { error.value = 'Completa email y contraseña'; return }
  loading.value = true
  try {
    const payload = {
      email: DOMPurify.sanitize(email.value),
      full_name: DOMPurify.sanitize(full_name.value || ''),
      password: password.value,
    }
    const { data } = await Auth.register(payload)
    localStorage.setItem('token', data.access_token)
    location.href = '/'
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error registrando'
  } finally { loading.value = false }
}
</script>

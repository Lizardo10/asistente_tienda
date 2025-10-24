<template>
  <div class="mx-auto" style="max-width:520px">
    <h3 class="mb-3">Recuperar contraseña</h3>
    <div class="card mb-3">
      <div class="card-body">
        <h6 class="card-title">1) Solicitar token</h6>
        <form @submit.prevent="requestT" class="row g-2">
          <div class="col-8"><input v-model.trim="email" type="email" class="form-control" placeholder="tu@correo.com" /></div>
          <div class="col-4"><button class="btn btn-outline-primary w-100" :disabled="loading1">Obtener token</button></div>
        </form>
        <div class="small text-muted mt-2">Para pruebas, el backend devuelve el token en la respuesta.</div>
        <div class="mt-2"><code v-if="token">{{ token }}</code></div>
      </div>
    </div>
    <div class="card">
      <div class="card-body">
        <h6 class="card-title">2) Confirmar</h6>
        <form @submit.prevent="confirmT" class="row g-2">
          <div class="col-12"><input v-model="token" class="form-control" placeholder="Pega aquí tu token" /></div>
          <div class="col-8"><input v-model="new_password" type="password" class="form-control" placeholder="Nueva contraseña" /></div>
          <div class="col-4"><button class="btn btn-success w-100" :disabled="loading2">Actualizar</button></div>
        </form>
        <div class="text-danger mt-2" v-if="error">{{ error }}</div>
        <div class="text-success mt-2" v-if="ok">¡Contraseña actualizada!</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Auth } from '../services/api'
const email = ref(''); const token = ref(''); const new_password = ref('')
const loading1 = ref(false); const loading2 = ref(false)
const error = ref(''); const ok = ref(false)
async function requestT(){
  error.value=''; ok.value=false; loading1.value=true
  try{ const { data } = await Auth.requestReset(email.value); token.value = data.token || '' }
  catch(e){ error.value = e?.response?.data?.detail || 'Error solicitando token' }
  finally{ loading1.value=false }
}
async function confirmT(){
  error.value=''; ok.value=false; loading2.value=true
  try{ await Auth.confirmReset(token.value, new_password.value); ok.value=true }
  catch(e){ error.value = e?.response?.data?.detail || 'Error confirmando' }
  finally{ loading2.value=false }
}
</script>

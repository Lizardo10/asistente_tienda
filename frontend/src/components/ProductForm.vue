<template>
  <form @submit.prevent="onSubmit" style="display:grid; gap:.5rem; max-width:520px;">
    <label>Título <input v-model="model.title" required /></label>
    <label>Precio <input v-model.number="model.price" type="number" step="0.01" min="0" required /></label>
    <label>Descripción <textarea v-model="model.description" rows="3" /></label>
    <label>Imagen principal (URL) <input v-model="model.image_url" placeholder="/media/archivo.jpg o https://..." /></label>
    <label style="display:flex; align-items:center; gap:.5rem;">
      <input type="checkbox" v-model="model.active" /> Activo
    </label>
    <div style="display:flex; gap:.5rem;">
      <button>{{ submitText }}</button>
      <button type="button" @click="$emit('cancel')">Cancelar</button>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch, computed } from 'vue'

const props = defineProps({
  value: { type: Object, default: () => ({ title:'', price:0, description:'', image_url:'', active:true }) },
  mode: { type: String, default: 'create' } // 'create' | 'edit'
})
const emit = defineEmits(['submit','cancel'])

const model = reactive({ ...props.value })
watch(() => props.value, v => Object.assign(model, v || {}))

const submitText = computed(() => props.mode === 'edit' ? 'Actualizar' : 'Crear')

function onSubmit() {
  emit('submit', { ...model })
}
</script>

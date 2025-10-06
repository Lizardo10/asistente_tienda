<template>
  <div style="border:1px solid #ddd; padding:1rem; border-radius:.5rem;">
    <div style="display:flex; gap:.5rem; margin-bottom:.5rem;">
      <input v-model="message" placeholder="Escribe tu duda..." @keydown.enter="sendMsg" style="flex:1;" />
      <button @click="connect" :disabled="connected">Conectar</button>
      <button @click="disconnect" :disabled="!connected">Cerrar</button>
    </div>
    <div style="height:260px; overflow:auto; border:1px solid #eee; padding:.5rem;">
      <div v-for="(m, i) in log" :key="i">
        <strong>{{ m.sender }}:</strong> {{ m.content }}
      </div>
    </div>
    <button @click="sendMsg" :disabled="!connected || !message">Enviar</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const ws = ref(null)
const connected = ref(false)
const chatId = ref(null)
const message = ref('')
const log = ref([])

function connect() {
  if (connected.value) return
  ws.value = new WebSocket((import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace('http','ws') + '/ws/support')
  ws.value.onopen = () => { connected.value = true }
  ws.value.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data)
      if (data.type === 'chat_opened') {
        chatId.value = data.chat_id
      } else if (data.type === 'bot') {
        log.value.push({ sender: 'bot', content: data.message })
      }
    } catch {
      log.value.push({ sender: 'bot', content: evt.data })
    }
  }
  ws.value.onclose = () => { connected.value = false }
}

function disconnect() {
  ws.value?.close()
}

function sendMsg() {
  if (!message.value) return
  log.value.push({ sender:'you', content: message.value })
  ws.value?.send(message.value)
  message.value = ''
}
</script>

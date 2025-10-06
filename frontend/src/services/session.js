import { reactive } from 'vue'
import { Auth } from './api'

export const session = reactive({
  user: null,
  token: localStorage.getItem('token') || null,
})

export async function loadMe() {
  if (!session.token) { session.user = null; return }
  try {
    const { data } = await Auth.me()
    session.user = data
  } catch {
    session.user = null
  }
}

export function setToken(t) {
  session.token = t
  if (t) localStorage.setItem('token', t)
  else   localStorage.removeItem('token')
}

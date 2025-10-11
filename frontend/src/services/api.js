import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000'
})

// token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// -------------------
// Productos
// -------------------
export const Products = {
  list() {
    return api.get('/products')
  },
  get(id) {
    return api.get(`/products/${id}`)
  },
  create(payload) {
    return api.post('/products', payload)           // 👈 necesario
  },
  update(id, payload) {
    return api.put(`/products/${id}`, payload)
  },
  remove(id) {
    return api.delete(`/products/${id}`)
  },
  listImages(id) {
    return api.get(`/products/${id}/images`)
  },
  uploadImage(id, file) {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/products/${id}/images`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  removeImage(id, imageId) {
    return api.delete(`/products/${id}/images/${imageId}`)
  },
}

// -------------------
// Auth (opcional)
// -------------------
export const Auth = {
  register(payload) { return api.post('/auth/register', payload) },
  login(payload)    { return api.post('/auth/login', payload) },
  me()              { return api.get('/auth/me') }
}

export const Orders = {
  create(payload) {
    return api.post('/orders', payload)
  },
  my() {
    return api.get('/orders/my')
  },
  detail(id) {
    return api.get(`/orders/${id}`)
  },
  // Admin: obtener todas las órdenes
  all() {
    return api.get('/orders')
  }
}


export default api

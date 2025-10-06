// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import ResetPassword from '../components/ResetPassword.vue'
import Admin from '../views/Admin.vue'
import { session, loadMe } from '../services/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/reset-password', component: ResetPassword },

    // Solo clientes autenticados (no admin)
    { path: '/cart', component: () => import('../views/CartView.vue') },
    { path: '/orders', component: () => import('../views/OrdersView.vue') },

    // Solo admin
    { path: '/admin', component: Admin },
  ],
})

router.beforeEach(async (to, from, next) => {
  // Siempre intenta cargar el usuario si hay token y aún no está cargado
  // (si tu loadMe ya maneja la ausencia de token, puedes llamarlo siempre)
  await loadMe()

  // Rutas solo para clientes (logueados y NO admin)
  if (to.path === '/cart' || to.path === '/orders') {
    if (!session.user) return next('/login')
    if (session.user?.is_admin) return next('/admin')
  }

  // Ruta solo para admin
  if (to.path === '/admin') {
    if (!session.user?.is_admin) return next('/login')
  }

  return next()
})

export default router

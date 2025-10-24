// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Homepage from '../views/Homepage.vue'
import Home from '../views/Home.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import ResetPassword from '../components/ResetPassword.vue'
import Admin from '../views/Admin.vue'
import { session, loadMe } from '../services/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Homepage },
    { path: '/products', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/reset-password', component: ResetPassword },
    { path: '/confirm-account', component: () => import('../views/AccountConfirmation.vue') },
    { path: '/confirm-email', component: () => import('../views/AccountConfirmation.vue') },
    

    // Chat avanzado (accesible para todos)
    { path: '/chat', component: () => import('../views/AdvancedChat.vue') },

    // Solo clientes autenticados (no admin)
    { path: '/cart', component: () => import('../views/CartView.vue') },
    { path: '/orders', component: () => import('../views/OrdersView.vue') },
    { path: '/checkout', component: () => import('../views/CheckoutView.vue') },
    { path: '/checkout/success', component: () => import('../views/CheckoutSuccessSimple.vue') },
    { path: '/checkout/cancel', component: () => import('../views/CheckoutCancel.vue') },

    // Solo admin
    { path: '/admin', component: Admin },
    { path: '/admin/accounting', component: () => import('../views/AccountingDashboard.vue') },
    { path: '/admin/financial', component: () => import('../views/AdminFinancial.vue') },
    { path: '/admin/chat-history', component: () => import('../views/ChatHistory.vue') },
    { path: '/admin/products', component: () => import('../views/AdminProducts.vue') },
    { path: '/admin/orders', component: () => import('../views/AdminOrders.vue') },
  ],
})

router.beforeEach(async (to, from, next) => {
  // Siempre intenta cargar el usuario si hay token y aún no está cargado
  // (si tu loadMe ya maneja la ausencia de token, puedes llamarlo siempre)
  await loadMe()

  // Rutas solo para clientes (logueados y NO admin)
  if (to.path === '/cart' || to.path === '/orders' || to.path === '/checkout' || to.path.startsWith('/checkout/')) {
    if (!session.user) return next('/login')
    if (session.user?.role === 'admin') return next('/admin')
  }

  // Rutas solo para admin
  if (to.path.startsWith('/admin')) {
    if (session.user?.role !== 'admin') return next('/login')
  }

  // Si ya está logueado, no puede acceder a login/register
  if ((to.path === '/login' || to.path === '/register' || to.path === '/reset-password') && session.user) {
    if (session.user?.role === 'admin') {
      return next('/admin')
    } else {
      return next('/products')
    }
  }

  return next()
})

export default router

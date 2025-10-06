<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom px-3">
      <router-link class="navbar-brand fw-semibold" to="/">🛍️ Tienda</router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#nav"
        aria-controls="nav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="nav" class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Productos</router-link>
          </li>

          <!-- Carrito visible solo para clientes (no admin) -->
          <li class="nav-item" v-if="isLoggedIn && !session.user?.is_admin">
            <router-link class="nav-link" to="/cart">Carrito <span class="badge bg-primary ms-1">{{ cartCount }}</span></router-link>
          </li>

          <li class="nav-item" v-if="isLoggedIn && !session.user?.is_admin">
            <router-link class="nav-link" to="/orders">Mis pedidos</router-link>
          </li>

          <!-- Solo visible si es admin -->
          <li class="nav-item" v-if="session.user?.is_admin">
            <router-link class="nav-link" to="/admin">Admin</router-link>
          </li>
        </ul>

        <!-- No autenticado -->
        <div class="d-flex gap-2" v-if="!isLoggedIn">
          <router-link class="btn btn-outline-primary btn-sm" to="/register">Registrarse</router-link>
          <router-link class="btn btn-primary btn-sm" to="/login">Iniciar sesión</router-link>
        </div>

        <!-- Autenticado -->
        <div class="d-flex align-items-center gap-3" v-else>
          <small class="text-muted d-none d-md-inline">
            {{ session.user?.email }}
            <span v-if="session.user?.is_admin" class="badge bg-secondary ms-1">Admin</span>
          </small>
          <button class="btn btn-outline-secondary btn-sm" @click="logout">Cerrar sesión</button>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { session, loadMe, setToken } from './services/session'
import { useRouter } from 'vue-router'

const router = useRouter()

// cargar usuario al iniciar la app (si hay token)
onMounted(() => { loadMe() })

const isLoggedIn = computed(() => !!session.token && !!session.user)

function logout () {
  setToken(null)
  router.push('/login')
}
</script>

<style>
/* Opcional: resalta link activo de la navbar */
.router-link-active.nav-link,
.router-link-exact-active.nav-link {
  font-weight: 600;
}
</style>

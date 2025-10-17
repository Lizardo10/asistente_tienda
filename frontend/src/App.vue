<template>
  <div>
    <nav class="navbar navbar-expand-lg custom-header shadow-sm px-3">
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
            <router-link class="nav-link" to="/cart">
              Carrito
              <span class="badge bg-light text-primary ms-1">{{ cartCount }}</span>
            </router-link>
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
          <router-link class="btn btn-outline-light btn-sm" to="/register">Registrarse</router-link>
          <router-link class="btn btn-outline-light btn-sm" to="/login">Iniciar sesión</router-link>
        </div>

        <!-- Autenticado -->
        <div class="d-flex align-items-center gap-3" v-else>
          <small class="text-light d-none d-md-inline">
            {{ session.user?.email }}
            <span v-if="session.user?.is_admin" class="badge bg-secondary ms-1">Admin</span>
          </small>
          <button class="btn btn-outline-light btn-sm" @click="logout">Cerrar sesión</button>
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

// Cargar usuario al iniciar la app
onMounted(() => { loadMe() })

const isLoggedIn = computed(() => !!session.token && !!session.user)

function logout () {
  setToken(null)
  router.push('/login')
}
</script>

<style>
/* resalta link activo */
.router-link-active.nav-link,
.router-link-exact-active.nav-link {
  font-weight: 600;
}
</style>

<style scoped>
.custom-header {
  background: linear-gradient(90deg, #007bff, #00c6ff); /* azul degradado */
  border: none;
  box-shadow: 0 2px 10px rgba(0, 123, 255, 0.3);
}

/* Textos del nav */
.navbar a,
.navbar-brand,
.nav-link {
  color: #fff !important;
}

/* Botones blancos contorneados */
.btn-outline-light {
  border-color: #fff;
  color: #fff;
  transition: all 0.3s ease;
}

.btn-outline-light:hover {
  background-color: #fff;
  color: #007bff;
}

/* badge del carrito */
.badge.bg-light.text-primary {
  font-size: 0.75rem;
}
</style>

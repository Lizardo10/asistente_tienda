<template>
  <div class="checkout-cancel-page">
    <div class="cancel-container">
      <div class="cancel-icon">
        <i class="fas fa-times-circle"></i>
      </div>
      
      <h1 class="cancel-title">Pago Cancelado</h1>
      <p class="cancel-message">El pago ha sido cancelado. Puedes intentar de nuevo cuando estés listo.</p>
      
      <div class="cancel-actions">
        <router-link to="/cart" class="btn-primary">
          <i class="fas fa-shopping-cart"></i>
          Volver al Carrito
        </router-link>
        <router-link to="/products" class="btn-secondary">
          <i class="fas fa-shopping-bag"></i>
          Continuar Comprando
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// No necesitamos lógica especial para la cancelación
</script>

<style scoped>
.checkout-cancel-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
}

.cancel-container {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.cancel-icon {
  font-size: 80px;
  color: #ef4444;
  margin-bottom: 20px;
}

.cancel-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 10px;
}

.cancel-message {
  font-size: 1.2rem;
  color: #6b7280;
  margin-bottom: 30px;
}

.cancel-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
  transform: translateY(-2px);
}

@media (max-width: 640px) {
  .cancel-container {
    padding: 30px 20px;
  }
  
  .cancel-title {
    font-size: 2rem;
  }
  
  .cancel-actions {
    flex-direction: column;
  }
  
  .btn-primary, .btn-secondary {
    justify-content: center;
  }
}
</style>
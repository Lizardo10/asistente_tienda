<template>
  <div class="min-h-screen bg-gradient-hero flex items-center justify-center p-4">
    <div class="max-w-4xl mx-auto text-center">
      <!-- Header -->
      <div class="mb-12">
        <h1 class="text-6xl font-display font-bold text-white mb-4 animate-float">
          🏪 Asistente Tienda
        </h1>
        <p class="text-xl text-white/90 font-sans">
          Sistema de chat inteligente funcionando correctamente
        </p>
      </div>

      <!-- Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <!-- Card 1 -->
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover-lift card-hover">
          <div class="text-4xl mb-4">🚀</div>
          <h3 class="text-xl font-semibold text-white mb-2">CDN Incluido</h3>
          <p class="text-white/80">Tailwind CSS CDN agregado al HTML</p>
        </div>

        <!-- Card 2 -->
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover-lift card-hover">
          <div class="text-4xl mb-4">⚙️</div>
          <h3 class="text-xl font-semibold text-white mb-2">Configuración</h3>
          <p class="text-white/80">Tailwind configurado con colores personalizados</p>
        </div>

        <!-- Card 3 -->
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover-lift card-hover">
          <div class="text-4xl mb-4">🎨</div>
          <h3 class="text-xl font-semibold text-white mb-2">Estilos</h3>
          <p class="text-white/80">Gradientes y animaciones personalizadas</p>
        </div>
      </div>

      <!-- Buttons -->
      <div class="flex flex-wrap justify-center gap-4 mb-8">
        <button class="bg-primary-500 hover:bg-primary-600 text-white px-8 py-3 rounded-xl font-semibold transition-all-smooth shadow-glow btn-animate">
          Botón Primario
        </button>
        <button class="bg-secondary-500 hover:bg-secondary-600 text-white px-8 py-3 rounded-xl font-semibold transition-all-smooth shadow-glow btn-animate">
          Botón Secundario
        </button>
        <button class="bg-white/20 hover:bg-white/30 text-white px-8 py-3 rounded-xl font-semibold transition-all-smooth backdrop-blur-lg border border-white/30 btn-animate">
          Botón Glass
        </button>
      </div>

      <!-- Status -->
      <div class="bg-green-500/20 border border-green-500/30 rounded-xl p-4 backdrop-blur-lg">
        <div class="flex items-center justify-center gap-2 text-green-300">
          <i class="fas fa-check-circle"></i>
          <span class="font-semibold">Tailwind CSS funcionando correctamente</span>
        </div>
      </div>

      <!-- Features List -->
      <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
        <div class="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
          <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <i class="fas fa-palette text-primary-400"></i>
            Características Incluidas
          </h4>
          <ul class="space-y-2 text-white/80">
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              CDN de Tailwind CSS
            </li>
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Google Fonts (Inter & Poppins)
            </li>
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Colores personalizados
            </li>
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Animaciones personalizadas
            </li>
          </ul>
        </div>

        <div class="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
          <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <i class="fas fa-magic text-secondary-400"></i>
            Efectos Disponibles
          </h4>
          <ul class="space-y-2 text-white/80">
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Glass morphism
            </li>
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Gradientes personalizados
            </li>
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Sombras con glow
            </li>
            <li class="flex items-center gap-2">
              <i class="fas fa-check text-green-400"></i>
              Hover effects
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TailwindTest',
  mounted() {
    console.log('🎨 Tailwind CSS Test Component mounted successfully!')
  }
}
</script>

<style scoped>
/* Estilos adicionales si es necesario */
</style>



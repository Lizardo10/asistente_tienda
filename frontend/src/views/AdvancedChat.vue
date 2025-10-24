<template>
  <div class="advanced-chat-view">
    <div class="chat-container">
      <div class="chat-info">
        <h1>🤖 Asistente Inteligente de Ventas</h1>
        <p>Pregunta sobre nuestros productos, precios, políticas de envío o cualquier duda que tengas. 
           Nuestro asistente AI está aquí para ayudarte de la manera más amable y profesional.</p>
        
        <div class="features">
          <div class="feature">
            <h3>🧠 Inteligencia Avanzada</h3>
            <p>Utiliza RAG (Retrieval-Augmented Generation) para proporcionar respuestas precisas basadas en nuestros productos y políticas.</p>
          </div>
          
          <div class="feature">
            <h3>💬 Conversación Contextual</h3>
            <p>Recuerda el contexto de la conversación para brindarte respuestas más relevantes y personalizadas.</p>
          </div>
          
          <div class="feature">
            <h3>🛍️ Recomendaciones Inteligentes</h3>
            <p>Sugiere productos específicos basándose en tus consultas y necesidades.</p>
          </div>
        </div>
      </div>
      
      <div class="chat-widget-container">
        <AdvancedChatWidget />
      </div>
    </div>
    
    <div class="chat-examples">
      <h2>💡 Ejemplos de preguntas que puedes hacer:</h2>
      <div class="examples-grid">
        <div class="example-category">
          <h3>🛒 Sobre Productos</h3>
          <ul>
            <li>¿Qué productos tienen disponibles?</li>
            <li>¿Cuál es el precio de [producto]?</li>
            <li>¿Tienen productos para [categoría]?</li>
            <li>¿Qué características tiene [producto]?</li>
          </ul>
        </div>
        
        <div class="example-category">
          <h3>💰 Sobre Precios y Pagos</h3>
          <ul>
            <li>¿Cuáles son sus métodos de pago?</li>
            <li>¿Ofrecen descuentos?</li>
            <li>¿Hay promociones especiales?</li>
            <li>¿Puedo pagar a plazos?</li>
          </ul>
        </div>
        
        <div class="example-category">
          <h3>🚚 Sobre Envíos</h3>
          <ul>
            <li>¿Cuánto cuesta el envío?</li>
            <li>¿En cuánto tiempo llega mi pedido?</li>
            <li>¿Envían a [ciudad]?</li>
            <li>¿Puedo hacer seguimiento de mi pedido?</li>
          </ul>
        </div>
        
        <div class="example-category">
          <h3>🔄 Sobre Devoluciones</h3>
          <ul>
            <li>¿Cuál es su política de devoluciones?</li>
            <li>¿Puedo cambiar un producto?</li>
            <li>¿Cuánto tiempo tengo para devolver?</li>
            <li>¿Cómo proceso una devolución?</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AdvancedChatWidget from '../components/AdvancedChatWidget.vue'
</script>

<style scoped>
.advanced-chat-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.chat-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  margin-bottom: 3rem;
}

.chat-info {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.chat-info h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 2rem;
}

.chat-info p {
  color: #7f8c8d;
  line-height: 1.6;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.features {
  display: grid;
  gap: 1.5rem;
}

.feature {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #3498db;
}

.feature h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.feature p {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

.chat-widget-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-examples {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.chat-examples h2 {
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
  font-size: 1.8rem;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.example-category {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  border-top: 4px solid #e74c3c;
}

.example-category h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.example-category ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.example-category li {
  background: white;
  margin-bottom: 0.5rem;
  padding: 0.75rem;
  border-radius: 8px;
  color: #34495e;
  font-size: 0.9rem;
  border-left: 3px solid #3498db;
  cursor: pointer;
  transition: all 0.2s;
}

.example-category li:hover {
  background: #e3f2fd;
  transform: translateX(4px);
}

/* Responsive */
@media (max-width: 768px) {
  .chat-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .advanced-chat-view {
    padding: 1rem;
  }
  
  .chat-info {
    padding: 1.5rem;
  }
  
  .chat-info h1 {
    font-size: 1.5rem;
  }
  
  .examples-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>



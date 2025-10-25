#!/usr/bin/env python3
"""
Script simple para probar las funciones de chat directamente
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def test_smart_response():
    """Prueba la función generate_smart_response directamente"""
    try:
        from app.services.openai_service import generate_smart_response
        from app.database.connection import get_db
        
        print("🧪 Probando función generate_smart_response directamente")
        print("=" * 60)
        
        # Obtener base de datos
        db = next(get_db())
        
        # Mensajes de prueba
        test_messages = [
            "Hola",
            "¿Qué productos tienen disponibles?",
            "¿Cuáles son sus precios?",
            "¿Cómo puedo hacer un pedido?",
            "¿Tienen envíos a domicilio?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Prueba {i}: '{message}'")
            
            try:
                response = generate_smart_response(message, db)
                print(f"✅ Respuesta: {response[:150]}...")
                
                # Verificar que contenga "Asistente Tienda"
                if "Asistente Tienda" in response:
                    print("✅ ✅ Nombre de la tienda correcto")
                else:
                    print("⚠️ ⚠️ Nombre de la tienda no encontrado")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("🏁 Pruebas completadas")
        
    except Exception as e:
        print(f"❌ Error importando funciones: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_response()

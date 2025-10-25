#!/usr/bin/env python3
"""
Script de prueba para verificar que el chat de Asistente Tienda funcione correctamente
"""

import requests
import json
import time

def test_chat_endpoint():
    """Prueba el endpoint del chat"""
    base_url = "http://localhost:8000"
    
    print("🏪 Probando Chat de Asistente Tienda")
    print("=" * 50)
    
    # Lista de mensajes de prueba
    test_messages = [
        "Hola",
        "¿Qué productos tienen disponibles?",
        "¿Cuáles son sus precios?",
        "¿Cómo puedo hacer un pedido?",
        "¿Tienen envíos a domicilio?",
        "¿Cuáles son sus horarios de atención?",
        "Necesito ayuda con mi compra"
    ]
    
    chat_id = 1
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Prueba {i}: '{message}'")
        
        try:
            # Enviar mensaje al chat
            response = requests.post(
                f"{base_url}/modern-chat/advanced-message",
                json={
                    "message": message,
                    "chat_id": chat_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get("response", "Sin respuesta")
                intent = data.get("intent", {})
                recommendations = data.get("recommendations", [])
                
                print(f"✅ Respuesta: {bot_response[:100]}...")
                print(f"🎯 Intención: {intent.get('type', 'unknown')}")
                print(f"📦 Recomendaciones: {len(recommendations)}")
                
                # Verificar que la respuesta contenga "Asistente Tienda"
                if "Asistente Tienda" in bot_response:
                    print("✅ ✅ Nombre de la tienda correcto")
                else:
                    print("⚠️ ⚠️ Nombre de la tienda no encontrado")
                
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
        
        # Pausa entre mensajes
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

def test_health_endpoint():
    """Prueba el endpoint de salud"""
    print("\n🔍 Verificando estado del backend...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend funcionando - Versión: {data.get('version', 'unknown')}")
            print(f"📊 Servicios: {data.get('services', {})}")
        else:
            print(f"❌ Backend con problemas - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al backend: {e}")

def test_frontend():
    """Prueba que el frontend esté funcionando"""
    print("\n🎨 Verificando frontend...")
    
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend funcionando correctamente")
        else:
            print(f"❌ Frontend con problemas - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al frontend: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del sistema Asistente Tienda")
    
    # Verificar servicios
    test_health_endpoint()
    test_frontend()
    
    # Probar chat
    test_chat_endpoint()
    
    print("\n🎉 ¡Pruebas completadas!")
    print("\n📋 Resumen:")
    print("• Backend: http://localhost:8000")
    print("• Frontend: http://localhost:5173")
    print("• Chat Mejorado: http://localhost:5173/enhanced-chat")
    print("• API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()

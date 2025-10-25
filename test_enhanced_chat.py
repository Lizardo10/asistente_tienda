#!/usr/bin/env python3
"""
Script de prueba para el chat mejorado
Verifica que OpenAI, audio e imágenes funcionen correctamente
"""
import requests
import base64
import json
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health():
    """Probar endpoint de salud"""
    print("🔍 Probando endpoint de salud...")
    try:
        response = requests.get(f"{API_BASE}/chat-enhanced/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Servicio de salud OK")
            print(f"   OpenAI: {data['services']['openai']}")
            print(f"   Audio: {data['services']['audio']}")
            print(f"   Imagen: {data['services']['image']}")
            return True
        else:
            print(f"❌ Error en salud: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False

def test_text_message():
    """Probar mensaje de texto"""
    print("\n💬 Probando mensaje de texto...")
    try:
        data = {
            "message": "Hola, ¿qué productos tienen disponibles?",
            "chat_id": 1,
            "message_type": "text"
        }
        response = requests.post(f"{API_BASE}/chat-enhanced/message", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje de texto OK")
            print(f"   Respuesta: {result['response'][:100]}...")
            print(f"   Recomendaciones: {len(result['recommendations'])}")
            return True
        else:
            print(f"❌ Error en mensaje de texto: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en mensaje de texto: {e}")
        return False

def test_audio_message():
    """Probar mensaje de audio"""
    print("\n🎤 Probando mensaje de audio...")
    try:
        # Crear un archivo de audio de prueba (silencioso)
        test_audio_data = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        
        data = {
            "audio_data": base64.b64encode(test_audio_data).decode('utf-8'),
            "chat_id": 1,
            "filename": "test.wav"
        }
        response = requests.post(f"{API_BASE}/chat-enhanced/audio", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje de audio OK")
            print(f"   Respuesta: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ Error en mensaje de audio: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en mensaje de audio: {e}")
        return False

def test_image_message():
    """Probar mensaje con imagen"""
    print("\n📸 Probando mensaje con imagen...")
    try:
        # Crear una imagen de prueba simple (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        data = {
            "image_data": base64.b64encode(test_image_data).decode('utf-8'),
            "chat_id": 1,
            "filename": "test.png"
        }
        response = requests.post(f"{API_BASE}/chat-enhanced/image", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje con imagen OK")
            print(f"   Respuesta: {result['response'][:100]}...")
            if result.get('image_analysis'):
                print(f"   Análisis: {result['image_analysis']['description'][:50]}...")
            return True
        else:
            print(f"❌ Error en mensaje con imagen: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en mensaje con imagen: {e}")
        return False

def test_upload_audio():
    """Probar subida de archivo de audio"""
    print("\n📁 Probando subida de archivo de audio...")
    try:
        # Crear archivo temporal
        test_audio_data = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        
        files = {
            'audio_file': ('test.wav', test_audio_data, 'audio/wav')
        }
        data = {
            'chat_id': 1
        }
        
        response = requests.post(f"{API_BASE}/chat-enhanced/upload-audio", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Subida de audio OK")
            print(f"   Respuesta: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ Error en subida de audio: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en subida de audio: {e}")
        return False

def test_upload_image():
    """Probar subida de archivo de imagen"""
    print("\n📁 Probando subida de archivo de imagen...")
    try:
        # Crear imagen de prueba
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'image_file': ('test.png', test_image_data, 'image/png')
        }
        data = {
            'chat_id': 1
        }
        
        response = requests.post(f"{API_BASE}/chat-enhanced/upload-image", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Subida de imagen OK")
            print(f"   Respuesta: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ Error en subida de imagen: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en subida de imagen: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del chat mejorado...")
    print("=" * 50)
    
    tests = [
        ("Salud del servicio", test_health),
        ("Mensaje de texto", test_text_message),
        ("Mensaje de audio", test_audio_message),
        ("Mensaje con imagen", test_image_message),
        ("Subida de audio", test_upload_audio),
        ("Subida de imagen", test_upload_image),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El chat mejorado está funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración de OpenAI y otros servicios.")
    
    print("\n💡 Para usar el chat mejorado:")
    print("   1. Ve a http://localhost:5173/enhanced-chat")
    print("   2. Configura tu OPENAI_API_KEY en backend/.env")
    print("   3. ¡Disfruta del chat inteligente!")

if __name__ == "__main__":
    main()



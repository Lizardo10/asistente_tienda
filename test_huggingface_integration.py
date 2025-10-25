"""
Script para probar la integración con Hugging Face
"""
import requests
import json
from PIL import Image
import io
import base64

def test_huggingface_integration():
    """Probar la integración con Hugging Face"""
    base_url = "http://localhost:8000"
    
    print("🤗 Probando integración con Hugging Face...")
    
    # 1. Probar estado del servicio
    print("\n1. Verificando estado del servicio...")
    try:
        response = requests.get(f"{base_url}/huggingface/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Estado del servicio: {status['status']}")
            print(f"   API Key configurada: {status['api_key_configured']}")
            print(f"   API URL: {status['api_url']}")
            print(f"   Modelos: CLIP={status['clip_model']}, BLIP={status['blip_model']}")
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # 2. Probar conexión con Hugging Face API
    print("\n2. Probando conexión con Hugging Face API...")
    try:
        response = requests.get(f"{base_url}/huggingface/test-connection")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Conexión exitosa: {result['message']}")
                print(f"   Tiempo de respuesta: {result.get('response_time', 'N/A')}s")
            else:
                print(f"⚠️ Conexión falló: {result['message']}")
                print(f"   Estado: {result['status']}")
        else:
            print(f"❌ Error probando conexión: {response.status_code}")
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
    
    # 3. Probar análisis de imagen básico
    print("\n3. Probando análisis de imagen básico...")
    try:
        # Crear una imagen de prueba simple
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        # Enviar imagen para análisis
        files = {'file': ('test_image.jpg', img_buffer, 'image/jpeg')}
        response = requests.post(f"{base_url}/image-search/search", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Análisis de imagen exitoso")
            print(f"   Descripción: {result['image_analysis']['description']}")
            print(f"   Productos encontrados: {result['total_found']}")
            print(f"   Método usado: {result['image_analysis'].get('method', 'N/A')}")
        else:
            print(f"❌ Error analizando imagen: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error probando análisis de imagen: {e}")
    
    print("\n🎯 Prueba de integración completada!")

if __name__ == "__main__":
    test_huggingface_integration()










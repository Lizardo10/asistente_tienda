"""
Script para configurar la API key de Hugging Face
"""
import os

def configure_huggingface():
    print("=== CONFIGURACIÓN DE HUGGING FACE ===")
    print()
    print("Para usar la API oficial de Hugging Face necesitas:")
    print("1. Ir a: https://huggingface.co/settings/tokens")
    print("2. Crear un token nuevo (es gratis)")
    print("3. Copiar el token")
    print()
    
    token = input("Pega tu token de Hugging Face aquí: ").strip()
    
    if not token:
        print("❌ No se proporcionó token")
        return
    
    if not token.startswith("hf_"):
        print("⚠️  El token debería empezar con 'hf_'")
        print("¿Estás seguro de que es correcto? (s/n): ", end="")
        if input().lower() != 's':
            return
    
    # Crear archivo .env si no existe
    env_path = ".env"
    env_content = ""
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Actualizar o agregar HUGGINGFACE_API_KEY
    lines = env_content.split('\n') if env_content else []
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('HUGGINGFACE_API_KEY='):
            lines[i] = f'HUGGINGFACE_API_KEY={token}'
            updated = True
            break
    
    if not updated:
        lines.append(f'HUGGINGFACE_API_KEY={token}')
    
    # Escribir archivo .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print()
    print("✅ API key configurada correctamente")
    print("🔄 Reinicia el servidor para aplicar los cambios")
    print()
    print("Para probar la configuración:")
    print("curl http://localhost:8000/huggingface/status")

if __name__ == "__main__":
    configure_huggingface()

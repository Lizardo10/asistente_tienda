"""
Script para reiniciar el servidor backend
"""
import subprocess
import time
import os

def restart_backend():
    print("=== REINICIANDO SERVIDOR BACKEND ===")
    print()
    
    # Cambiar al directorio backend
    os.chdir("backend")
    
    # Activar entorno virtual
    print("Activando entorno virtual...")
    activate_script = "venv\\Scripts\\activate"
    
    # Comando para reiniciar el servidor
    cmd = f"{activate_script} && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    print("Iniciando servidor backend...")
    print("Comando:", cmd)
    print()
    print("El servidor se iniciará en http://localhost:8000")
    print("Presiona Ctrl+C para detener el servidor")
    print()
    
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nServidor detenido.")

if __name__ == "__main__":
    restart_backend()










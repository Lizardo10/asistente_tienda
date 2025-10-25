#!/usr/bin/env python3
"""
Script para reiniciar el backend de Asistente Tienda
"""

import subprocess
import sys
import os
import time
import signal
import psutil

def kill_existing_processes():
    """Mata procesos existentes del backend"""
    print("🔄 Deteniendo procesos existentes...")
    
    # Buscar procesos de uvicorn
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'uvicorn' in proc.info['name'].lower():
                print(f"   Terminando proceso: {proc.info['pid']} - {proc.info['name']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    
    # Buscar procesos de Python que ejecuten main.py
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('main.py' in cmd for cmd in proc.info['cmdline']):
                print(f"   Terminando proceso Python: {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    
    time.sleep(2)
    print("✅ Procesos detenidos")

def start_backend():
    """Inicia el backend"""
    print("🚀 Iniciando Asistente Tienda Backend...")
    
    # Cambiar al directorio del backend
    backend_dir = os.path.join(os.getcwd(), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ Error: No se encontró el directorio backend/")
        return False
    
    os.chdir(backend_dir)
    
    # Verificar que existe main.py
    if not os.path.exists('app/main.py'):
        print("❌ Error: No se encontró app/main.py")
        return False
    
    # Comando para iniciar el servidor
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--reload', 
        '--host', '0.0.0.0', 
        '--port', '8000'
    ]
    
    print(f"📡 Ejecutando: {' '.join(cmd)}")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 API Docs en: http://localhost:8000/docs")
    print("🏪 Asistente Tienda iniciado correctamente!")
    print("\n" + "="*60)
    print("Presiona Ctrl+C para detener el servidor")
    print("="*60 + "\n")
    
    try:
        # Ejecutar el comando
        process = subprocess.run(cmd, check=True)
        return True
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🏪 Asistente Tienda - Reinicio del Backend")
    print("=" * 50)
    
    # Detener procesos existentes
    kill_existing_processes()
    
    # Iniciar backend
    success = start_backend()
    
    if success:
        print("✅ Backend reiniciado correctamente")
    else:
        print("❌ Error al reiniciar el backend")
        sys.exit(1)

if __name__ == "__main__":
    main()

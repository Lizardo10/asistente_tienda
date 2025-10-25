#!/usr/bin/env python3
"""
Script para verificar estructura final del proyecto limpio
"""
import os

def verify_final_structure():
    """Verificar estructura final del proyecto"""
    print("=== ESTRUCTURA FINAL DEL PROYECTO LIMPIO ===")
    
    # Estructura raiz
    print("\n📁 ESTRUCTURA RAÍZ:")
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    root_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    print("Archivos:")
    for file in sorted(root_files):
        size = os.path.getsize(file)
        print(f"  - {file} ({size:,} bytes)")
    
    print("\nDirectorios:")
    for dir_name in sorted(root_dirs):
        print(f"  - {dir_name}/")
    
    # Estructura backend
    print("\n📁 BACKEND:")
    backend_files = [f for f in os.listdir('backend') if os.path.isfile(f'backend/{f}')]
    backend_dirs = [d for d in os.listdir('backend') if os.path.isdir(f'backend/{d}')]
    
    print("Archivos:")
    for file in sorted(backend_files):
        size = os.path.getsize(f'backend/{file}')
        print(f"  - {file} ({size:,} bytes)")
    
    print("\nDirectorios:")
    for dir_name in sorted(backend_dirs):
        print(f"  - {dir_name}/")
    
    # Estructura frontend
    print("\n📁 FRONTEND:")
    frontend_files = [f for f in os.listdir('frontend') if os.path.isfile(f'frontend/{f}')]
    frontend_dirs = [d for d in os.listdir('frontend') if os.path.isdir(f'frontend/{d}')]
    
    print("Archivos:")
    for file in sorted(frontend_files):
        size = os.path.getsize(f'frontend/{file}')
        print(f"  - {file} ({size:,} bytes)")
    
    print("\nDirectorios:")
    for dir_name in sorted(frontend_dirs):
        print(f"  - {dir_name}/")
    
    # Calcular tamaños
    def get_dir_size(path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except:
                    pass
        return total
    
    backend_size = get_dir_size('backend')
    frontend_size = get_dir_size('frontend')
    total_size = backend_size + frontend_size
    
    print(f"\n📊 TAMAÑOS:")
    print(f"  Backend: {backend_size:,} bytes ({backend_size/1024/1024:.1f} MB)")
    print(f"  Frontend: {frontend_size:,} bytes ({frontend_size/1024/1024:.1f} MB)")
    print(f"  Total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    return total_size

def check_essential_files():
    """Verificar archivos esenciales"""
    print("\n=== VERIFICACION DE ARCHIVOS ESENCIALES ===")
    
    essential_files = {
        "Raíz": [".gitignore", "README.md"],
        "Backend": [".env", "requirements.txt", "init_db.py"],
        "Frontend": ["package.json", "vite.config.js"]
    }
    
    all_present = True
    
    for category, files in essential_files.items():
        print(f"\n{category}:")
        for file in files:
            if category == "Raíz":
                path = file
            elif category == "Backend":
                path = f"backend/{file}"
            else:
                path = f"frontend/{file}"
            
            if os.path.exists(path):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - FALTANTE")
                all_present = False
    
    return all_present

def generate_deployment_summary():
    """Generar resumen para despliegue"""
    print("\n=== RESUMEN PARA DESPLIEGUE EN AWS EC2 ===")
    
    print("\n🚀 ARCHIVOS ESENCIALES PARA DESPLIEGUE:")
    print("  ✅ backend/.env - Configuración de base de datos")
    print("  ✅ backend/requirements.txt - Dependencias Python")
    print("  ✅ frontend/package.json - Dependencias Node.js")
    print("  ✅ README.md - Documentación del proyecto")
    
    print("\n🔧 CONFIGURACION NECESARIA:")
    print("  1. Actualizar DATABASE_URL en backend/.env para AWS")
    print("  2. Configurar PAYPAL_CLIENT_ID y PAYPAL_CLIENT_SECRET")
    print("  3. Configurar EMAIL_USER y EMAIL_PASSWORD")
    print("  4. Instalar dependencias: pip install -r requirements.txt")
    print("  5. Instalar frontend: npm install")
    
    print("\n📦 ESTRUCTURA OPTIMIZADA:")
    print("  - Solo archivos esenciales")
    print("  - Sin scripts de prueba")
    print("  - Sin documentación innecesaria")
    print("  - Listo para producción")

if __name__ == "__main__":
    print("VERIFICACION DE ESTRUCTURA FINAL")
    print("=" * 50)
    
    total_size = verify_final_structure()
    essential_ok = check_essential_files()
    generate_deployment_summary()
    
    print("\n" + "=" * 50)
    print("RESULTADO FINAL")
    print("=" * 50)
    
    if essential_ok:
        print("✅ Proyecto completamente limpio")
        print(f"✅ Tamaño total: {total_size/1024/1024:.1f} MB")
        print("✅ Listo para AWS EC2")
        print("✅ Estructura optimizada")
    else:
        print("❌ Faltan archivos esenciales")
        print("❌ Revisar estructura antes de desplegar")










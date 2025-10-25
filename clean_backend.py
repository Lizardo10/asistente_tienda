#!/usr/bin/env python3
"""
Script para limpiar directorio backend
"""
import os

def clean_backend():
    """Limpiar directorio backend"""
    print("=== LIMPIANDO DIRECTORIO BACKEND ===")
    
    # Archivos a eliminar del backend
    files_to_delete = [
        # Archivos de documentacion
        "ACCOUNTING_AREA_COMPLETE.md", "AUTHENTICATION_IMPROVEMENTS_COMPLETE.md",
        "BREVO_EMAIL_SYSTEM_COMPLETE.md", "BUSQUEDA_IMAGEN_MEJORADA.md",
        "CLEAN_ARCHITECTURE_COMPLETE.md", "CLEAN_ARCHITECTURE_GUIDE.md",
        "HUGGINGFACE_SETUP.md", "OAUTH_IMPLEMENTATION_COMPLETE.md",
        "PASSWORD_RESET_ERROR_FIXED.md", "PAYPAL_CONFIGURATION_GUIDE.md",
        "PROJECT_COMPLETE_FEATURES.md", "REINICIAR_SERVIDOR.md",
        "SISTEMA_CACHE_AVANZADO.md",
        
        # Scripts de creacion de datos
        "add_10_more_products.py", "add_balance_migration.py",
        "create_100_products.py", "create_100_products_direct.py",
        "create_100_products_simple.py", "create_admin_user.py",
        "create_client_with_history.py", "create_inactive_products.py",
        "create_sample_products.py", "create_users_simple.py",
        
        # Scripts de demo y test
        "demo_auth_system.py", "demo_basic_auth.py", "demo_complete_auth.py",
        "diagnose_rag_system.py", "simulate_frontend_request.py",
        "temp_confirmation_endpoint.py",
        
        # Scripts de migracion
        "migrate_chat_messages.py", "migrate_database.py",
        "migrate_orders_paypal.py", "migrate_products_add_fields.py",
        "migrate_products_postgresql.py", "update_chat_messages_metadata.py",
        "update_products_categories.py",
        
        # Scripts de verificacion
        "check_paypal_config.py", "check_paypal_simple.py",
        "check_products.py", "check_products_simple.py",
        "check_redis_data.py", "verify_final_products.py",
        
        # Scripts de test
        "test_admin_products.py", "test_advanced_features.py",
        "test_all_features.py", "test_audio_endpoint.py",
        "test_audio_simple.py", "test_audio_system.py",
        "test_auth_complete.py", "test_brevo.py",
        "test_cache_service.py", "test_chat_endpoints.py",
        "test_chat_rag_system.py", "test_complete_password_reset.py",
        "test_creative_products.py", "test_email_direct.py",
        "test_email_system.py", "test_endpoint_real.py",
        "test_final_audio.py", "test_frontend_registration.py",
        "test_frontend_simulation.py", "test_modern_chat.py",
        "test_modern_chat_fixed.py", "test_new_registration_flow.py",
        "test_openai.py", "test_openai_whisper.py",
        "test_openai_whisper_real.py", "test_password_reset.py",
        "test_paypal_integration.py", "test_postgresql_real.py",
        "test_postgresql_simple.py", "test_products_endpoints.py",
        "test_rag_corrected.py", "test_rag_system.py",
        "test_real_audio.py", "test_redis_cache.py",
        "test_redis_direct.py", "test_redis_sync.py",
        "test_redis_working.py", "test_sendgrid.py",
        "test_simple_chat.py", "test_simple_register.py",
        "test_websocket.py", "test_websocket_debug.py",
        "test_websocket_openai.py",
        
        # Scripts de inicio
        "start_backend.py", "start_simple_backend.py",
        "run_simple.py", "server_demo.py",
        
        # Scripts de configuracion
        "setup_paypal.py", "setup_postgresql.py",
        "simple_init.py",
        
        # Archivos innecesarios
        "nul", "tienda.db", "package-lock.json",
        "email_config_template.txt", "oauth_env_example.txt",
        ".env.backup"
    ]
    
    deleted = 0
    
    for file in files_to_delete:
        file_path = f"backend/{file}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"OK - {file}")
                deleted += 1
            except Exception as e:
                print(f"ERROR - {file}: {e}")
        else:
            print(f"INFO - {file} no existe")
    
    print(f"\nArchivos eliminados del backend: {deleted}")
    
    # Verificar estructura final del backend
    print("\n=== ESTRUCTURA FINAL DEL BACKEND ===")
    backend_files = [f for f in os.listdir('backend') if os.path.isfile(f'backend/{f}')]
    backend_dirs = [d for d in os.listdir('backend') if os.path.isdir(f'backend/{d}')]
    
    print("Archivos restantes:")
    for file in sorted(backend_files):
        print(f"  - {file}")
    
    print("\nDirectorios:")
    for dir_name in sorted(backend_dirs):
        print(f"  - {dir_name}/")
    
    return deleted

if __name__ == "__main__":
    print("LIMPIEZA DEL DIRECTORIO BACKEND")
    print("=" * 40)
    
    deleted = clean_backend()
    
    print("\n" + "=" * 40)
    print("LIMPIEZA DEL BACKEND COMPLETADA")
    print("=" * 40)
    print(f"Archivos eliminados: {deleted}")
    print("Backend optimizado para AWS EC2")










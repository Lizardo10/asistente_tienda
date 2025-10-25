#!/usr/bin/env python3
"""
Script para limpieza completa del proyecto para AWS EC2
"""
import os
import shutil

def clean_project():
    """Limpiar proyecto completamente"""
    print("=== LIMPIEZA COMPLETA DEL PROYECTO PARA AWS EC2 ===")
    
    # Archivos a eliminar (categorizados)
    files_to_delete = {
        "Scripts de prueba": [
            "activate_and_test.py", "activate_user_manually.py", "add_balance.py",
            "check_all_users.py", "check_balance.py", "check_database_tables.py",
            "check_db.py", "check_endpoints.py", "check_products.py", "check_recent_users.py",
            "check_users_table.py", "check_user_in_db.py", "check_user_type.py",
            "complete_solution.py", "confirm_email_direct.py", "create_and_activate_user.py",
            "create_new_user.py", "create_specific_user.py", "create_user_correct_hash.py",
            "create_user_with_token.py", "create_user_with_your_token.py", "create_working_user.py",
            "debug_checkout.py", "debug_order.py", "diagnose_paypal.py", "diagnose_paypal_simple.py",
            "final_solution.py", "fix_email_confirmation.py", "fix_user_confirmation.py",
            "get_working_credentials.py", "migrate_frontend.py", "nul", "restart_and_test_paypal.py",
            "review_database_system.py", "start_backend_8000.py", "start_backend_final.py",
            "start_backend_simple.py", "start_clean_architecture_app.py", "start_complete_app.py",
            "start_final_app.py", "start_final_fixed.py", "start_fixed_app.py",
            "start_modern_app.py", "start_original_app.py", "start_perfect_app.py",
            "start_simple_modern.py", "validate_modernization.py"
        ],
        
        "Scripts de test": [
            "test_admin_permissions.py", "test_admin_system.py", "test_all_features.py",
            "test_audio_formats.py", "test_auth_endpoints.py", "test_auth_me.py",
            "test_available_endpoints.py", "test_cart_clearing.py", "test_chat_endpoints.py",
            "test_chat_endpoints_updated.py", "test_chat_final.py", "test_checkout_final.py",
            "test_checkout_simple.py", "test_complete_admin_system.py", "test_complete_cart_clearing.py",
            "test_complete_chat_flow.py", "test_complete_confirmation_flow.py",
            "test_complete_email_confirmation.py", "test_complete_email_confirmation_real.py",
            "test_complete_email_flow.py", "test_complete_fixed_system.py", "test_complete_flow.py",
            "test_complete_flow_simple.py", "test_complete_registration_endpoint.py",
            "test_complete_registration_flow.py", "test_complete_system.py", "test_confirmation_direct_sql.py",
            "test_confirmation_existing_user.py", "test_confirmation_real_token.py",
            "test_confirm_email.py", "test_corrections.py", "test_corrections_simple.py",
            "test_correct_dev.py", "test_dev_mode.py", "test_direct_auth_me.py",
            "test_direct_confirmation.py", "test_direct_login.py", "test_email_confirmation_debug.py",
            "test_email_confirmation_simple.py", "test_email_simple.py", "test_email_system.py",
            "test_endpoint_real.py", "test_final_admin_system.py", "test_final_confirmation.py",
            "test_final_email_confirmation.py", "test_final_image_system.py", "test_final_paypal.py",
            "test_final_system.py", "test_frontend_confirmation.py", "test_frontend_endpoints.py",
            "test_frontend_health.py", "test_frontend_simulation.py", "test_full_recommendations.py",
            "test_image_analysis.py", "test_image_simple.py", "test_login_correct.py",
            "test_login_simulation.py", "test_modern_chat_real.py", "test_openai_whisper.py",
            "test_openai_whisper_real.py", "test_original_checkout.py", "test_password.py",
            "test_paypal_button.py", "test_paypal_complete.py", "test_paypal_db_user.py",
            "test_paypal_existing_user.py", "test_paypal_final.py", "test_paypal_final_db.py",
            "test_paypal_integration.py", "test_paypal_only.py", "test_paypal_production_ready.py",
            "test_paypal_production_simple.py", "test_paypal_quick.py", "test_paypal_simple.py",
            "test_paypal_simple_final.py", "test_paypal_temp_activation.py", "test_paypal_with_activation.py",
            "test_paypal_with_pepe.py", "test_products_fixed.py", "test_product_recommendations.py",
            "test_real_image.py", "test_real_paypal_user.py", "test_real_whisper.py",
            "test_recommendations_direct.py", "test_sandbox_complete.py", "test_sendinblue_api.py",
            "test_simple_admin.py", "test_simple_complete.py", "test_simple_fixed.py",
            "test_simple_recommendation.py", "test_sqlalchemy_checkout.py", "test_sqlmodel_user.py",
            "test_success_page.py", "test_system_status.py", "test_verify_password.py",
            "test_with_real_products.py", "test_with_real_token.py", "test_your_token.py",
            "test_your_user.py"
        ],
        
        "Scripts de verificacion": [
            "verify_after_sqlite_deletion.py", "verify_app.py", "verify_app_postgresql.py",
            "verify_before_delete_sqlite.py", "verify_complete_system.py", "verify_final_app.py",
            "verify_paypal_credentials.py", "verify_paypal_only.py", "verify_postgresql.py",
            "verify_postgresql_simple.py", "verify_redis.py"
        ],
        
        "Scripts de configuracion": [
            "configure_paypal_credentials.py", "configure_paypal_live.py", "configure_paypal_live_final.py",
            "configure_paypal_live_simple.py"
        ],
        
        "Archivos de documentacion innecesarios": [
            "AUTHENTICATION_IMPLEMENTATION_COMPLETE.md", "BACKEND_AND_LOGIN_SOLUTION.md",
            "CHAT_422_ERRORS_FIXED.md", "CHAT_FUNCIONANDO.md", "CHAT_LISTO_FINAL.md",
            "FINAL_SSR_FIXES.md", "FRONTEND_MODERN_CORRECTIONS.md", "FRONTEND_MODERN_FIXED.md",
            "FRONTEND_MODERN_WITH_OLD_FUNCTIONALITY.md", "LOGIN_BUTTONS_SOLUTION.md",
            "MODERNIZATION_COMPLETE.md", "MODERNIZATION_SUMMARY.md", "NAVBAR_DEBUG_SOLUTION.md",
            "NAVBAR_FIXED_COMPLETE.md", "PAYPAL_INTEGRATION_COMPLETE.md", "PROYECTO_100_COMPLETO.md",
            "PROYECTO_COMPLETO_FINAL.md", "PROYECTO_FINALIZADO.md", "README_MODERN.md",
            "README_PATCH.txt", "README_PROYECTO_FINAL.md", "README_RAG_SYSTEM.md",
            "SETUP_POSTGRESQL.md", "SOLUCION_CHAT_404.md", "SSR_ERRORS_FIXED.md",
            "SYNTAX_ERROR_FIXED.md"
        ],
        
        "Scripts de inicio innecesarios": [
            "start_backend.bat", "start_frontend.bat", "start_project.bat", "start_simple.bat"
        ]
    }
    
    # Archivos a mantener
    files_to_keep = [
        "README.md", ".gitignore", "backend", "frontend"
    ]
    
    total_deleted = 0
    
    # Eliminar archivos por categoria
    for category, files in files_to_delete.items():
        print(f"\nEliminando {category}...")
        category_deleted = 0
        
        for file in files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"  OK - {file}")
                    category_deleted += 1
                    total_deleted += 1
                except Exception as e:
                    print(f"  ERROR - {file}: {e}")
            else:
                print(f"  INFO - {file} no existe")
        
        print(f"  {category_deleted} archivos eliminados")
    
    print(f"\nTotal de archivos eliminados: {total_deleted}")
    
    # Verificar estructura final
    print("\n=== ESTRUCTURA FINAL ===")
    remaining_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    remaining_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    print("Archivos restantes:")
    for file in sorted(remaining_files):
        print(f"  - {file}")
    
    print("\nDirectorios:")
    for dir_name in sorted(remaining_dirs):
        print(f"  - {dir_name}/")
    
    return total_deleted

def clean_backend_directory():
    """Limpiar directorio backend"""
    print("\n=== LIMPIANDO DIRECTORIO BACKEND ===")
    
    backend_files_to_delete = [
        "email_system_improved.py"
    ]
    
    deleted = 0
    for file in backend_files_to_delete:
        file_path = f"backend/{file}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"OK - {file_path}")
                deleted += 1
            except Exception as e:
                print(f"ERROR - {file_path}: {e}")
    
    print(f"Archivos eliminados del backend: {deleted}")

if __name__ == "__main__":
    print("LIMPIEZA COMPLETA PARA AWS EC2")
    print("=" * 50)
    
    total_deleted = clean_project()
    clean_backend_directory()
    
    print("\n" + "=" * 50)
    print("LIMPIEZA COMPLETADA")
    print("=" * 50)
    print(f"Total archivos eliminados: {total_deleted}")
    print("Proyecto listo para AWS EC2")
    print("Estructura limpia y optimizada")










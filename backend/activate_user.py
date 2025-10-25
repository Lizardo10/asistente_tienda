#!/usr/bin/env python3
"""
Script para activar usuarios manualmente en la base de datos
Útil cuando el servicio de email no está configurado
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def activate_user(email: str):
    """Activar un usuario por email usando SQL directo"""
    from app.database.connection import engine
    from sqlalchemy import text
    
    try:
        with engine.connect() as conn:
            # Verificar si el usuario existe
            result = conn.execute(
                text("SELECT id, email, full_name, active, email_verified FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()
            
            if not user:
                print(f"❌ No se encontró usuario con email: {email}")
                return False
            
            print(f"📋 Usuario encontrado:")
            print(f"   - ID: {user[0]}")
            print(f"   - Email: {user[1]}")
            print(f"   - Nombre: {user[2]}")
            print(f"   - Activo: {user[3]}")
            print(f"   - Email verificado: {user[4]}")
            
            # Activar usuario
            conn.execute(
                text("UPDATE users SET active = true, email_verified = true, email_confirmation_token = NULL WHERE email = :email"),
                {"email": email}
            )
            conn.commit()
            
            print(f"\n✅ Usuario {email} activado exitosamente")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al activar usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_users():
    """Listar todos los usuarios usando SQL directo"""
    from app.database.connection import engine
    from sqlalchemy import text
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, email, full_name, active, email_verified FROM users ORDER BY id")
            )
            users = result.fetchall()
            
            if not users:
                print("📋 No hay usuarios en la base de datos")
                return
            
            print(f"📋 Lista de usuarios ({len(users)}):")
            print("-" * 100)
            print(f"{'Estado':<10} | {'Email':<40} | {'Nombre':<30} | ID")
            print("-" * 100)
            
            for user in users:
                status = "✅ Activo" if user[3] and user[4] else "❌ Inactivo"
                email = user[1] if user[1] else "Sin email"
                name = user[2] if user[2] else "Sin nombre"
                print(f"{status:<10} | {email:<40} | {name:<30} | {user[0]}")
            
    except Exception as e:
        print(f"❌ Error al listar usuarios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Activar usuarios manualmente")
    parser.add_argument("email", nargs="?", help="Email del usuario a activar")
    parser.add_argument("--list", action="store_true", help="Listar todos los usuarios")
    
    args = parser.parse_args()
    
    if args.list:
        list_users()
    elif args.email:
        activate_user(args.email)
    else:
        print("❌ Error: Debes especificar un email o usar --list")
        print("\nEjemplos de uso:")
        print("  python activate_user.py usuario@ejemplo.com")
        print("  python activate_user.py --list")
        sys.exit(1)

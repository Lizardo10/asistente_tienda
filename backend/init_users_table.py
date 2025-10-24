#!/usr/bin/env python3
"""
Inicializar solo las tablas básicas necesarias para el sistema de confirmación
"""
from app.db import engine, SessionLocal
from app.models_sqlmodel.user import User
from app.auth_enhanced import hash_password
from sqlalchemy.orm import Session
from datetime import datetime
import sqlalchemy as sa

def create_users_table():
    """Crear solo la tabla de usuarios"""
    try:
        # Crear la tabla users usando SQLAlchemy directamente
        from app.models_sqlmodel.user import User
        
        # Crear la tabla
        User.metadata.create_all(bind=engine)
        print("✅ Tabla 'users' creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla users: {e}")
        return False

def create_admin_user():
    """Crear usuario administrador"""
    db = SessionLocal()
    try:
        # Verificar si ya existe el admin
        existing_admin = db.query(User).filter(User.email == "pepe@gmail.com").first()
        if existing_admin:
            print("✅ Usuario administrador ya existe")
            return existing_admin
        
        # Crear usuario administrador
        admin_user = User(
            email="pepe@gmail.com",
            full_name="Pepe Admin",
            password_hash=hash_password("12345678"),
            role="admin",
            is_admin=True,
            active=True,
            email_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuario administrador creado exitosamente")
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def main():
    """Función principal"""
    try:
        print("🚀 Inicializando tabla de usuarios...")
        
        # Crear tabla de usuarios
        if create_users_table():
            # Crear usuario administrador
            admin_user = create_admin_user()
            
            if admin_user:
                print(f"\n🎉 Tabla de usuarios inicializada correctamente!")
                print(f"👤 Usuario administrador: {admin_user.email}")
                print(f"🔑 Contraseña: 12345678")
                print(f"🆔 ID: {admin_user.id}")
            else:
                print("❌ Error creando usuario administrador")
                return 1
        else:
            print("❌ Error creando tabla de usuarios")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        return 1

if __name__ == "__main__":
    exit(main())



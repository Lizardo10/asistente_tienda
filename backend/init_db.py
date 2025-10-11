from app.db import Base, engine, SessionLocal
from app import models
from app.auth_utils import hash_password
from datetime import datetime

def create_tables():
    """Crear todas las tablas de la base de datos"""
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tablas creadas exitosamente")

def create_sample_data():
    """Crear datos de ejemplo para la aplicación"""
    db = SessionLocal()
    try:
        # Verificar si ya existen datos
        existing_users = db.query(models.User).count()
        if existing_users > 0:
            print("[INFO] Ya existen datos en la base de datos. Saltando creacion de datos de ejemplo.")
            return

        print("Creando datos de ejemplo...")

        # 1. Crear usuarios
        admin_user = models.User(
            email="admin@tienda.com",
            full_name="Administrador",
            hashed_password=hash_password("admin123"),
            is_admin=True
        )
        
        customer_user = models.User(
            email="cliente@ejemplo.com",
            full_name="Cliente Ejemplo",
            hashed_password=hash_password("cliente123"),
            is_admin=False
        )

        db.add(admin_user)
        db.add(customer_user)
        db.commit()

        print("[OK] Usuarios creados")

        # 2. Crear productos
        products_data = [
            {
                "title": "Laptop Gaming Pro",
                "description": "Laptop de alto rendimiento para gaming y trabajo profesional",
                "price": 1299.99,
                "image_url": "/media/laptop.jpg"
            },
            {
                "title": "Smartphone Ultra",
                "description": "Teléfono inteligente con cámara de 108MP y batería de larga duración",
                "price": 899.99,
                "image_url": "/media/smartphone.jpg"
            },
            {
                "title": "Auriculares Inalámbricos",
                "description": "Auriculares con cancelación de ruido y sonido de alta calidad",
                "price": 299.99,
                "image_url": "/media/headphones.jpg"
            },
            {
                "title": "Tablet Pro",
                "description": "Tablet ideal para trabajo y entretenimiento",
                "price": 599.99,
                "image_url": "/media/tablet.jpg"
            },
            {
                "title": "Smartwatch Fitness",
                "description": "Reloj inteligente con seguimiento de salud y fitness",
                "price": 199.99,
                "image_url": "/media/smartwatch.jpg"
            }
        ]

        for product_data in products_data:
            product = models.Product(**product_data)
            db.add(product)

        db.commit()
        print("[OK] Productos creados")

        # 3. Crear una orden de ejemplo
        order = models.Order(
            user_id=customer_user.id,
            status="completed"
        )
        db.add(order)
        db.commit()

        # Agregar items a la orden
        products = db.query(models.Product).all()
        if products:
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=products[0].id,
                quantity=2,
                price_each=products[0].price
            )
            db.add(order_item)
            db.commit()

        print("[OK] Orden de ejemplo creada")

        # 4. Crear un chat de ejemplo
        chat = models.Chat(
            user_id=customer_user.id,
            status="closed"
        )
        db.add(chat)
        db.commit()

        # Agregar mensajes al chat
        messages = [
            {
                "chat_id": chat.id,
                "sender": "user",
                "content": "Hola, tengo una pregunta sobre el envío de mi pedido"
            },
            {
                "chat_id": chat.id,
                "sender": "bot",
                "content": "Hola! Te ayudo con tu consulta sobre el envío. ¿Cuál es el número de tu pedido?"
            },
            {
                "chat_id": chat.id,
                "sender": "user",
                "content": "Mi pedido es el #1"
            },
            {
                "chat_id": chat.id,
                "sender": "agent",
                "content": "Perfecto, veo que tu pedido ya fue procesado y está en camino. Llegará en 2-3 días hábiles."
            }
        ]

        for msg_data in messages:
            message = models.ChatMessage(**msg_data)
            db.add(message)

        db.commit()
        print("[OK] Chat de ejemplo creado")

        print("\n[EXITO] Base de datos inicializada con datos de ejemplo!")
        print("\nCredenciales de acceso:")
        print("   Admin: admin@tienda.com / admin123")
        print("   Cliente: cliente@ejemplo.com / cliente123")

    except Exception as e:
        print(f"[ERROR] Error creando datos de ejemplo: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Función principal para inicializar la base de datos"""
    try:
        create_tables()
        create_sample_data()
    except Exception as e:
        print(f"[ERROR] Error durante la inicializacion: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())

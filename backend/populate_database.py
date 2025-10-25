#!/usr/bin/env python3
"""
Script para poblar la base de datos con productos, categorías y usuario admin
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine
from sqlalchemy import text
from datetime import datetime
import random
import json

def create_admin_user():
    """Crear usuario administrador"""
    print("👤 Creando usuario administrador...")
    
    admin_data = {
        "email": "admin@tienda.com",
        "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K8K",  # admin123
        "full_name": "Administrador Tienda",
        "is_admin": True,
        "active": True,
        "email_verified": True,
        "mfa_enabled": False,
        "role": "admin",
        "balance": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    with engine.connect() as conn:
        # Verificar si ya existe
        result = conn.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": admin_data["email"]}
        )
        if result.fetchone():
            print("✅ Usuario admin ya existe")
            return
        
        # Crear usuario admin
        conn.execute(
            text("""
                INSERT INTO users (email, password_hash, full_name, is_admin, active, email_verified, 
                                 mfa_enabled, role, balance, created_at, updated_at)
                VALUES (:email, :password, :full_name, :is_admin, :active, :email_verified, 
                        :mfa_enabled, :role, :balance, :created_at, :updated_at)
            """),
            admin_data
        )
        conn.commit()
        print("✅ Usuario administrador creado exitosamente")

def create_categories():
    """Crear categorías de productos"""
    print("📂 Creando categorías...")
    
    categories = [
        {"name": "Electrónicos", "description": "Dispositivos electrónicos y tecnología"},
        {"name": "Ropa", "description": "Ropa para hombres, mujeres y niños"},
        {"name": "Hogar y Jardín", "description": "Artículos para el hogar y jardín"},
        {"name": "Deportes", "description": "Equipos y accesorios deportivos"},
        {"name": "Libros", "description": "Libros y material educativo"},
        {"name": "Belleza", "description": "Productos de belleza y cuidado personal"},
        {"name": "Automotriz", "description": "Accesorios y repuestos para vehículos"},
        {"name": "Juguetes", "description": "Juguetes para niños de todas las edades"},
        {"name": "Alimentación", "description": "Productos alimenticios y bebidas"},
        {"name": "Mascotas", "description": "Productos para mascotas"},
        {"name": "Oficina", "description": "Artículos de oficina y papelería"},
        {"name": "Salud", "description": "Productos de salud y bienestar"},
        {"name": "Viajes", "description": "Accesorios de viaje y maletas"},
        {"name": "Música", "description": "Instrumentos musicales y accesorios"},
        {"name": "Arte", "description": "Materiales de arte y manualidades"}
    ]
    
    with engine.connect() as conn:
        for cat in categories:
            # Verificar si ya existe
            result = conn.execute(
                text("SELECT id FROM categories WHERE name = :name"),
                {"name": cat["name"]}
            )
            if result.fetchone():
                continue
            
            conn.execute(
                text("""
                    INSERT INTO categories (name, description, created_at, updated_at)
                    VALUES (:name, :description, :created_at, :updated_at)
                """),
                {
                    "name": cat["name"],
                    "description": cat["description"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        conn.commit()
        print(f"✅ {len(categories)} categorías creadas")

def create_products():
    """Crear 300 productos con datos realistas"""
    print("🛍️ Creando 300 productos...")
    
    # Obtener categorías
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM categories"))
        categories = result.fetchall()
        category_ids = [cat[0] for cat in categories]
    
    # Productos por categoría
    products_data = {
        "Electrónicos": [
            {"name": "iPhone 15 Pro", "price": 999.99, "description": "Smartphone Apple con cámara profesional"},
            {"name": "MacBook Air M2", "price": 1199.99, "description": "Laptop ultradelgada con chip M2"},
            {"name": "Samsung Galaxy S24", "price": 899.99, "description": "Smartphone Android de última generación"},
            {"name": "iPad Pro 12.9", "price": 1099.99, "description": "Tablet profesional para creativos"},
            {"name": "AirPods Pro", "price": 249.99, "description": "Audífonos inalámbricos con cancelación de ruido"},
            {"name": "Apple Watch Series 9", "price": 399.99, "description": "Smartwatch con GPS y monitor de salud"},
            {"name": "Sony WH-1000XM5", "price": 399.99, "description": "Audífonos con cancelación de ruido líder"},
            {"name": "Nintendo Switch OLED", "price": 349.99, "description": "Consola de videojuegos portátil"},
            {"name": "PlayStation 5", "price": 499.99, "description": "Consola de videojuegos de nueva generación"},
            {"name": "Xbox Series X", "price": 499.99, "description": "Consola de videojuegos de Microsoft"},
            {"name": "Dell XPS 13", "price": 1299.99, "description": "Laptop premium para profesionales"},
            {"name": "LG OLED C3", "price": 1299.99, "description": "TV OLED 4K de 55 pulgadas"},
            {"name": "Canon EOS R6", "price": 2499.99, "description": "Cámara mirrorless profesional"},
            {"name": "DJI Mini 3 Pro", "price": 759.99, "description": "Drone compacto para fotografía aérea"},
            {"name": "GoPro Hero 12", "price": 399.99, "description": "Cámara de acción 4K"},
            {"name": "Samsung QLED QN90A", "price": 1999.99, "description": "TV QLED 4K de 65 pulgadas"},
            {"name": "Bose QuietComfort 45", "price": 329.99, "description": "Audífonos con cancelación de ruido"},
            {"name": "Steam Deck", "price": 399.99, "description": "Consola portátil para PC gaming"},
            {"name": "Meta Quest 3", "price": 499.99, "description": "Gafas de realidad virtual"},
            {"name": "Tesla Model 3", "price": 39999.99, "description": "Automóvil eléctrico sedán"}
        ],
        "Ropa": [
            {"name": "Camiseta Nike Dri-FIT", "price": 29.99, "description": "Camiseta deportiva transpirable"},
            {"name": "Jeans Levis 501", "price": 89.99, "description": "Jeans clásicos de mezclilla"},
            {"name": "Zapatillas Adidas Ultraboost", "price": 180.99, "description": "Zapatillas deportivas con tecnología Boost"},
            {"name": "Chaqueta North Face", "price": 199.99, "description": "Chaqueta impermeable para outdoor"},
            {"name": "Vestido Zara", "price": 39.99, "description": "Vestido elegante para ocasiones especiales"},
            {"name": "Sudadera Champion", "price": 49.99, "description": "Sudadera cómoda con capucha"},
            {"name": "Pantalón Hugo Boss", "price": 149.99, "description": "Pantalón de vestir elegante"},
            {"name": "Zapatos Timberland", "price": 159.99, "description": "Botas resistentes para outdoor"},
            {"name": "Reloj Casio G-Shock", "price": 99.99, "description": "Reloj resistente a golpes y agua"},
            {"name": "Bolso Louis Vuitton", "price": 1299.99, "description": "Bolso de lujo de cuero"},
            {"name": "Cinturón Gucci", "price": 399.99, "description": "Cinturón de cuero de lujo"},
            {"name": "Gafas Ray-Ban", "price": 149.99, "description": "Gafas de sol clásicas"},
            {"name": "Traje Hugo Boss", "price": 599.99, "description": "Traje de negocios elegante"},
            {"name": "Falda Mango", "price": 29.99, "description": "Falda moderna y versátil"},
            {"name": "Blusa H&M", "price": 19.99, "description": "Blusa casual para el día a día"},
            {"name": "Chaqueta bomber", "price": 79.99, "description": "Chaqueta bomber estilo vintage"},
            {"name": "Pantalones cargo", "price": 59.99, "description": "Pantalones cargo con múltiples bolsillos"},
            {"name": "Sneakers Converse", "price": 65.99, "description": "Zapatillas clásicas de lona"},
            {"name": "Sombrero New Era", "price": 34.99, "description": "Gorra de béisbol oficial"},
            {"name": "Bufanda Burberry", "price": 299.99, "description": "Bufanda de lujo con estampado clásico"}
        ],
        "Hogar y Jardín": [
            {"name": "Aspiradora Dyson V15", "price": 649.99, "description": "Aspiradora inalámbrica de alta potencia"},
            {"name": "Robot aspirador iRobot", "price": 399.99, "description": "Robot aspirador automático"},
            {"name": "Cafetera Nespresso", "price": 199.99, "description": "Máquina de café por cápsulas"},
            {"name": "Freidora de aire Philips", "price": 149.99, "description": "Freidora sin aceite saludable"},
            {"name": "Licuadora Vitamix", "price": 449.99, "description": "Licuadora profesional de alta velocidad"},
            {"name": "Horno microondas Samsung", "price": 299.99, "description": "Microondas con tecnología inverter"},
            {"name": "Refrigerador LG", "price": 1299.99, "description": "Refrigerador con dispensador de agua"},
            {"name": "Lavadora Samsung", "price": 799.99, "description": "Lavadora con tecnología EcoBubble"},
            {"name": "Secadora Whirlpool", "price": 699.99, "description": "Secadora de ropa eficiente"},
            {"name": "Aspiradora Shark", "price": 199.99, "description": "Aspiradora vertical potente"},
            {"name": "Purificador de aire Dyson", "price": 549.99, "description": "Purificador de aire con filtro HEPA"},
            {"name": "Ventilador Dyson", "price": 399.99, "description": "Ventilador sin aspas"},
            {"name": "Calentador de agua", "price": 299.99, "description": "Calentador de agua eléctrico"},
            {"name": "Aspiradora central", "price": 899.99, "description": "Sistema de aspirado central"},
            {"name": "Máquina de hielo", "price": 199.99, "description": "Máquina automática de hielo"},
            {"name": "Exprimidor de naranjas", "price": 79.99, "description": "Exprimidor eléctrico para cítricos"},
            {"name": "Tostadora KitchenAid", "price": 129.99, "description": "Tostadora de 4 rebanadas"},
            {"name": "Olla de presión Instant Pot", "price": 99.99, "description": "Olla de presión eléctrica multifunción"},
            {"name": "Batidora KitchenAid", "price": 299.99, "description": "Batidora de pie profesional"},
            {"name": "Mesa de comedor", "price": 599.99, "description": "Mesa de comedor para 6 personas"}
        ],
        "Deportes": [
            {"name": "Pelota de fútbol Nike", "price": 29.99, "description": "Pelota oficial de fútbol"},
            {"name": "Raqueta de tenis Wilson", "price": 199.99, "description": "Raqueta profesional de tenis"},
            {"name": "Bicicleta Trek", "price": 899.99, "description": "Bicicleta de montaña de aluminio"},
            {"name": "Pesas Bowflex", "price": 299.99, "description": "Set de pesas ajustables"},
            {"name": "Cinta de correr NordicTrack", "price": 999.99, "description": "Cinta de correr motorizada"},
            {"name": "Bicicleta estática Peloton", "price": 1495.99, "description": "Bicicleta estática con pantalla"},
            {"name": "Gimnasio en casa", "price": 499.99, "description": "Máquina multifunción para gimnasio"},
            {"name": "Yoga mat Lululemon", "price": 78.99, "description": "Colchoneta de yoga premium"},
            {"name": "Proteína Whey Gold Standard", "price": 49.99, "description": "Proteína en polvo para deportistas"},
            {"name": "Zapatillas running Asics", "price": 129.99, "description": "Zapatillas para correr"},
            {"name": "Gafas de natación Speedo", "price": 24.99, "description": "Gafas de natación profesionales"},
            {"name": "Tabla de surf", "price": 399.99, "description": "Tabla de surf para principiantes"},
            {"name": "Raqueta de pádel", "price": 149.99, "description": "Raqueta de pádel profesional"},
            {"name": "Pelota de baloncesto Spalding", "price": 39.99, "description": "Pelota oficial de baloncesto"},
            {"name": "Guantes de boxeo Everlast", "price": 59.99, "description": "Guantes de boxeo profesionales"},
            {"name": "Casco de ciclismo Giro", "price": 89.99, "description": "Casco de seguridad para ciclismo"},
            {"name": "Mochila de senderismo Osprey", "price": 149.99, "description": "Mochila para trekking"},
            {"name": "Botas de montaña Salomon", "price": 199.99, "description": "Botas de senderismo"},
            {"name": "Reloj deportivo Garmin", "price": 299.99, "description": "Reloj GPS para deportes"},
            {"name": "Cuerda de escalada", "price": 79.99, "description": "Cuerda dinámica para escalada"}
        ],
        "Libros": [
            {"name": "El Quijote", "price": 19.99, "description": "Obra maestra de Miguel de Cervantes"},
            {"name": "Cien años de soledad", "price": 16.99, "description": "Novela de Gabriel García Márquez"},
            {"name": "1984", "price": 14.99, "description": "Distopía clásica de George Orwell"},
            {"name": "El Principito", "price": 12.99, "description": "Cuento filosófico de Antoine de Saint-Exupéry"},
            {"name": "Don Juan Tenorio", "price": 11.99, "description": "Drama romántico de José Zorrilla"},
            {"name": "La Celestina", "price": 13.99, "description": "Tragicomedia de Fernando de Rojas"},
            {"name": "Lazarillo de Tormes", "price": 10.99, "description": "Novela picaresca anónima"},
            {"name": "Platero y yo", "price": 9.99, "description": "Prosa poética de Juan Ramón Jiménez"},
            {"name": "La casa de Bernarda Alba", "price": 11.99, "description": "Drama de Federico García Lorca"},
            {"name": "El amor en los tiempos del cólera", "price": 15.99, "description": "Novela de Gabriel García Márquez"},
            {"name": "Rayuela", "price": 18.99, "description": "Novela experimental de Julio Cortázar"},
            {"name": "Ficciones", "price": 14.99, "description": "Cuentos de Jorge Luis Borges"},
            {"name": "La ciudad y los perros", "price": 16.99, "description": "Novela de Mario Vargas Llosa"},
            {"name": "Pedro Páramo", "price": 13.99, "description": "Novela de Juan Rulfo"},
            {"name": "La tregua", "price": 12.99, "description": "Novela de Mario Benedetti"},
            {"name": "El túnel", "price": 11.99, "description": "Novela psicológica de Ernesto Sábato"},
            {"name": "La invención de Morel", "price": 10.99, "description": "Novela de ciencia ficción de Adolfo Bioy Casares"},
            {"name": "El Aleph", "price": 13.99, "description": "Cuentos de Jorge Luis Borges"},
            {"name": "Los detectives salvajes", "price": 19.99, "description": "Novela de Roberto Bolaño"},
            {"name": "El obsceno pájaro de la noche", "price": 17.99, "description": "Novela de José Donoso"}
        ]
    }
    
    # Crear productos adicionales para llegar a 300
    additional_products = []
    for category_name, products in products_data.items():
        additional_products.extend(products)
    
    # Generar productos adicionales aleatorios
    while len(additional_products) < 300:
        category_id = random.choice(category_ids)
        category_name = next(cat[1] for cat in categories if cat[0] == category_id)
        
        # Generar nombres y descripciones aleatorios
        prefixes = ["Premium", "Pro", "Elite", "Standard", "Deluxe", "Ultra", "Max", "Super"]
        suffixes = ["2024", "Plus", "Advanced", "Classic", "Modern", "Vintage", "Sport", "Luxury"]
        
        name = f"{random.choice(prefixes)} {category_name[:-1]} {random.choice(suffixes)}"
        price = round(random.uniform(19.99, 999.99), 2)
        description = f"Producto de alta calidad en la categoría {category_name}"
        
        additional_products.append({
            "name": name,
            "price": price,
            "description": description,
            "category_id": category_id
        })
    
    # Insertar productos en la base de datos
    with engine.connect() as conn:
        for i, product in enumerate(additional_products[:300]):
            # Verificar si ya existe
            result = conn.execute(
                text("SELECT id FROM products WHERE title = :title"),
                {"title": product["name"]}
            )
            if result.fetchone():
                continue
            
            conn.execute(
                text("""
                    INSERT INTO products (title, description, price, category, stock, 
                                        active, created_at, updated_at)
                    VALUES (:title, :description, :price, :category, :stock, 
                            :active, :created_at, :updated_at)
                """),
                {
                    "title": product["name"],
                    "description": product["description"],
                    "price": product["price"],
                    "category": category_name,
                    "stock": random.randint(10, 100),
                    "active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            
            if (i + 1) % 50 == 0:
                print(f"✅ {i + 1} productos creados...")
        
        conn.commit()
        print(f"✅ {min(300, len(additional_products))} productos creados exitosamente")

def create_rag_knowledge_base():
    """Crear base de conocimiento para RAG"""
    print("🧠 Creando base de conocimiento RAG...")
    
    knowledge_data = [
        {
            "title": "Política de Envíos",
            "content": "Ofrecemos envío gratuito en compras superiores a $50. Los envíos estándar tardan 3-5 días hábiles. Para envíos express (1-2 días), el costo es de $15 adicionales.",
            "category": "shipping"
        },
        {
            "title": "Política de Devoluciones",
            "content": "Aceptamos devoluciones hasta 30 días después de la compra. Los productos deben estar en su estado original con etiquetas. El reembolso se procesa en 5-7 días hábiles.",
            "category": "returns"
        },
        {
            "title": "Garantía de Productos",
            "content": "Todos nuestros productos tienen garantía del fabricante. Los productos electrónicos tienen garantía de 1 año. Para activar la garantía, contacta con nuestro servicio al cliente.",
            "category": "warranty"
        },
        {
            "title": "Métodos de Pago",
            "content": "Aceptamos tarjetas de crédito Visa, Mastercard, American Express. También PayPal, Apple Pay, Google Pay y transferencias bancarias. Todos los pagos son seguros y encriptados.",
            "category": "payment"
        },
        {
            "title": "Horarios de Atención",
            "content": "Nuestro servicio al cliente está disponible de lunes a viernes de 9:00 AM a 6:00 PM, y sábados de 10:00 AM a 4:00 PM. Puedes contactarnos por chat, email o teléfono.",
            "category": "support"
        },
        {
            "title": "Productos Destacados",
            "content": "Nuestros productos más populares incluyen smartphones iPhone y Samsung, laptops MacBook y Dell, zapatillas Nike y Adidas, y productos de hogar Dyson y Samsung.",
            "category": "products"
        },
        {
            "title": "Ofertas Especiales",
            "content": "Tenemos ofertas especiales todos los viernes. Descuentos del 20% en electrónicos, 15% en ropa, y 10% en hogar. También ofrecemos descuentos por volumen en compras empresariales.",
            "category": "offers"
        },
        {
            "title": "Programa de Fidelidad",
            "content": "Únete a nuestro programa de fidelidad y gana puntos en cada compra. 1 punto por cada dólar gastado. Los puntos se pueden canjear por descuentos o productos gratuitos.",
            "category": "loyalty"
        }
    ]
    
    with engine.connect() as conn:
        for knowledge in knowledge_data:
            # Verificar si ya existe
            result = conn.execute(
                text("SELECT id FROM rag_knowledge WHERE title = :title"),
                {"title": knowledge["title"]}
            )
            if result.fetchone():
                continue
            
            conn.execute(
                text("""
                    INSERT INTO rag_knowledge (title, content, category, created_at, updated_at)
                    VALUES (:title, :content, :category, :created_at, :updated_at)
                """),
                {
                    "title": knowledge["title"],
                    "content": knowledge["content"],
                    "category": knowledge["category"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        conn.commit()
        print(f"✅ {len(knowledge_data)} entradas de conocimiento RAG creadas")

def main():
    """Función principal"""
    print("🚀 Iniciando población de la base de datos...")
    
    try:
        create_admin_user()
        create_categories()
        create_products()
        create_rag_knowledge_base()
        
        print("\n🎉 ¡Base de datos poblada exitosamente!")
        print("\n📊 Resumen:")
        print("   👤 Usuario admin: admin@tienda.com / admin123")
        print("   📂 Categorías: 15")
        print("   🛍️ Productos: 300")
        print("   🧠 Conocimiento RAG: 8 entradas")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

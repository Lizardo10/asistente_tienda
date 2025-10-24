#!/usr/bin/env python3
"""
Script para poblar la base de datos con productos de ejemplo
para que el sistema RAG tenga datos con los que trabajar.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, engine
from app.models import Base, Product, ProductImage
from sqlalchemy.orm import Session

def create_sample_products():
    """Crea productos de ejemplo con descripciones detalladas"""
    
    sample_products = [
        {
            "title": "Laptop Gaming ASUS ROG",
            "description": "Laptop gaming de alto rendimiento con procesador Intel i7, 16GB RAM, tarjeta gráfica NVIDIA RTX 4060, pantalla de 15.6 pulgadas Full HD 144Hz. Perfecta para gaming y trabajo profesional. Incluye teclado RGB, webcam HD y sistema de audio premium.",
            "price": 1299.99,
            "image_url": "/media/gaming-laptop.jpg"
        },
        {
            "title": "Smartphone Samsung Galaxy S24",
            "description": "Smartphone flagship con pantalla AMOLED de 6.2 pulgadas, procesador Snapdragon 8 Gen 3, 256GB de almacenamiento, cámara triple de 50MP con zoom óptico 3x, batería de 4000mAh con carga rápida inalámbrica. Resistente al agua IP68.",
            "price": 899.99,
            "image_url": "/media/smartphone.jpg"
        },
        {
            "title": "Auriculares Sony WH-1000XM5",
            "description": "Auriculares inalámbricos premium con cancelación de ruido líder en la industria, 30 horas de batería, carga rápida de 3 minutos para 3 horas de uso. Sonido de alta fidelidad con drivers de 30mm, compatibles con Alexa y Google Assistant.",
            "price": 399.99,
            "image_url": "/media/headphones.jpg"
        },
        {
            "title": "Tablet iPad Air 11 pulgadas",
            "description": "Tablet profesional con chip M2, pantalla Liquid Retina de 11 pulgadas, 256GB de almacenamiento, cámara frontal Ultra Wide de 12MP, compatible con Apple Pencil y Magic Keyboard. Ideal para creativos y profesionales.",
            "price": 699.99,
            "image_url": "/media/tablet.jpg"
        },
        {
            "title": "Smartwatch Apple Watch Series 9",
            "description": "Reloj inteligente con GPS, monitor de frecuencia cardíaca, SpO2, detección de caídas y llamadas de emergencia. Pantalla Always-On Retina, resistente al agua hasta 50 metros. Batería de hasta 18 horas de duración.",
            "price": 449.99,
            "image_url": "/media/smartwatch.jpg"
        },
        {
            "title": "Monitor Gaming 27 pulgadas 4K",
            "description": "Monitor gaming de 27 pulgadas con resolución 4K UHD, frecuencia de actualización de 144Hz, tiempo de respuesta de 1ms, soporte para HDR10, puertos DisplayPort y HDMI. Tecnología FreeSync Premium Pro para gaming sin tearing.",
            "price": 599.99,
            "image_url": "/media/monitor.jpg"
        },
        {
            "title": "Cámara Canon EOS R6 Mark II",
            "description": "Cámara mirrorless profesional con sensor full-frame de 24.2MP, grabación de video 4K 60fps, estabilización de imagen de 8 stops, autofoco inteligente con seguimiento de ojos y animales. Perfecta para fotografía y videografía profesional.",
            "price": 2499.99,
            "image_url": "/media/camera.jpg"
        },
        {
            "title": "Teclado Mecánico Logitech MX Keys",
            "description": "Teclado inalámbrico ergonómico con retroiluminación inteligente, teclas de perfil bajo para escritura cómoda, conectividad USB-C y Bluetooth, batería de hasta 5 meses de duración. Compatible con Windows, Mac y Linux.",
            "price": 99.99,
            "image_url": "/media/keyboard.jpg"
        },
        {
            "title": "Mouse Gaming Razer DeathAdder V3",
            "description": "Mouse gaming de precisión con sensor óptico de 30,000 DPI, 90 horas de batería, diseño ergonómico para diestros, switches ópticos de 90 millones de clics, conectividad inalámbrica de baja latencia.",
            "price": 79.99,
            "image_url": "/media/mouse.jpg"
        },
        {
            "title": "Altavoces Bluetooth JBL Charge 5",
            "description": "Altavoz portátil resistente al agua IP67, 20 horas de reproducción, carga inalámbrica, función PartyBoost para conectar múltiples altavoces, graves potentes con driver de 65mm. Perfecto para fiestas y actividades al aire libre.",
            "price": 149.99,
            "image_url": "/media/speaker.jpg"
        }
    ]
    
    return sample_products

def populate_database():
    """Pobla la base de datos con productos de ejemplo"""
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Verificar si ya hay productos
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"Ya existen {existing_products} productos en la base de datos.")
            return
        
        # Obtener productos de ejemplo
        sample_products = create_sample_products()
        
        # Insertar productos
        for product_data in sample_products:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        print(f"Se insertaron {len(sample_products)} productos de ejemplo exitosamente.")
        
        # Mostrar resumen
        print("\nProductos agregados:")
        products = db.query(Product).all()
        for product in products:
            print(f"  - {product.title} - ${product.price:.2f}")
            
    except Exception as e:
        db.rollback()
        print(f"Error al poblar la base de datos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando poblacion de base de datos con productos de ejemplo...")
    populate_database()
    print("Completado!")

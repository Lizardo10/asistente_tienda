import asyncio
import sys
import os

from app.services.rag_service import rag_service

async def test_rag():
    print('=== Probando RAG Service ===')
    
    # Probar búsqueda de conocimiento
    print('\n1. Probando búsqueda de conocimiento:')
    knowledge = await rag_service.search_knowledge('envío')
    print(f'Resultados encontrados: {len(knowledge)}')
    for item in knowledge:
        print(f'- {item["title"]}: {item["content"][:100]}...')
    
    # Probar búsqueda de productos
    print('\n2. Probando búsqueda de productos:')
    products = await rag_service.search_products('camiseta')
    print(f'Productos encontrados: {len(products)}')
    for product in products[:3]:
        print(f'- {product["title"]} (${product["price"]})')
    
    # Probar generación de respuesta
    print('\n3. Probando generación de respuesta:')
    response = await rag_service.generate_response('¿Qué camisetas tienes disponibles?')
    print(f'Respuesta RAG: {response}')
    
    # Probar recomendaciones
    print('\n4. Probando recomendaciones:')
    recommendations = await rag_service.get_recommendations('camiseta')
    print(f'Recomendaciones: {len(recommendations)}')
    for rec in recommendations[:2]:
        print(f'- {rec["title"]} (${rec["price"]})')

if __name__ == "__main__":
    asyncio.run(test_rag())
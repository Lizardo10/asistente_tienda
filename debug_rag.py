import asyncio
from app.services.rag_service import rag_service

async def debug_rag():
    print('=== Debug RAG Service ===')
    
    # Probar búsqueda de productos específicamente
    print('\nBuscando productos con "camiseta":')
    products = await rag_service.search_products('camiseta')
    print(f'Productos encontrados: {len(products)}')
    for product in products:
        print(f'- {product["title"]} (${product["price"]}) - Stock: {product["stock"]}')
    
    # Probar get_recommendations
    print('\nProbando get_recommendations:')
    recommendations = await rag_service.get_recommendations('camiseta')
    print(f'Recomendaciones: {len(recommendations)}')
    for rec in recommendations:
        print(f'- {rec["title"]} (${rec["price"]})')

if __name__ == "__main__":
    asyncio.run(debug_rag())





from typing import List, Dict, Optional
from app.database.connection import engine
from sqlalchemy import text
import openai
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def search_knowledge(self, query: str, limit: int = 3) -> List[Dict]:
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text('SELECT title, content, category FROM rag_knowledge WHERE LOWER(title) LIKE LOWER(:query) OR LOWER(content) LIKE LOWER(:query) LIMIT :limit'),
                    {'query': f'%{query}%', 'limit': limit}
                )
                knowledge_items = []
                for row in result:
                    knowledge_items.append({'title': row[0], 'content': row[1], 'category': row[2]})
                return knowledge_items
        except Exception as e:
            print(f'Error buscando conocimiento: {e}')
            return []
    
    async def search_products(self, query: str, limit: int = 5) -> List[Dict]:
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text('SELECT id, title, description, price, category, stock FROM products WHERE active = true AND (LOWER(title) LIKE LOWER(:query) OR LOWER(description) LIKE LOWER(:query) OR LOWER(category) LIKE LOWER(:query)) LIMIT :limit'),
                    {'query': f'%{query}%', 'limit': limit}
                )
                products = []
                for row in result:
                    products.append({'id': row[0], 'title': row[1], 'description': row[2], 'price': float(row[3]), 'category': row[4], 'stock': row[5]})
                return products
        except Exception as e:
            print(f'Error buscando productos: {e}')
            return []
    
    async def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
        try:
            knowledge = await self.search_knowledge(user_message)
            products = await self.search_products(user_message)
            
            context_text = ''
            if knowledge:
                context_text += 'Información de la tienda:\n'
                for item in knowledge:
                    context_text += f'- {item["title"]}: {item["content"]}\n'
                context_text += '\n'
            
            if products:
                context_text += 'Productos disponibles:\n'
                for product in products[:3]:
                    context_text += f'- {product["title"]}: ${product["price"]} ({product["category"]})\n'
                context_text += '\n'
            
            system_prompt = f'Eres un asistente virtual de una tienda online. Usa la siguiente información para responder de manera útil y amigable: {context_text} Instrucciones: - Responde en español - Sé amigable y profesional - Si hay productos relevantes, menciónalos - Si no tienes información específica, ofrece ayuda general - Mantén las respuestas concisas pero útiles'
            
            response = self.openai_client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f'Error generando respuesta RAG: {e}')
            return 'Lo siento, no pude procesar tu consulta en este momento. ¿Podrías reformular tu pregunta?'
    
    async def get_recommendations(self, user_message: str) -> List[Dict]:
        try:
            products = await self.search_products(user_message, limit=5)
            return products
        except Exception as e:
            print(f'Error obteniendo recomendaciones: {e}')
            return []

rag_service = RAGService()

async def rag_answer(query: str, db=None, context: List[Dict] = None) -> str:
    return await rag_service.generate_response(query, context)

async def advanced_rag_answer(query: str, db=None, context: List[Dict] = None) -> Dict:
    try:
        response = await rag_service.generate_response(query, context)
        recommendations = await rag_service.get_recommendations(query)
        return {'response': response, 'recommendations': recommendations, 'context': context or []}
    except Exception as e:
        return {'response': f'Lo siento, no pude procesar tu consulta: {str(e)}', 'recommendations': [], 'context': []}
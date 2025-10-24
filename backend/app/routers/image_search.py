"""
Router para búsqueda de productos por imagen
Usa Hugging Face para análisis de imágenes
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db import get_db
from app import models
from app.services.huggingface_image_service import huggingface_image_service
from app.services.ai_service import ai_service

router = APIRouter(prefix="/products/search", tags=["Product Search"])
image_search_router = APIRouter(prefix="/image-search", tags=["Image Search"])


@router.post("/by-image")
async def search_products_by_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Buscar productos similares usando una imagen"""
    try:
        # Leer imagen
        image_data = await file.read()
        
        # Analizar imagen con Hugging Face
        print(f"Analizando imagen: {file.filename}")
        analysis = huggingface_image_service.analyze_image(image_data)
        
        if not analysis["success"]:
            raise HTTPException(status_code=400, detail="Error analizando la imagen")
        
        # Obtener descripción de la imagen
        image_description = analysis["description"]
        print(f"Descripcion generada: {image_description}")
        
        # Obtener todos los productos
        products = db.query(models.Product).filter(models.Product.active == True).all()
        
        # Buscar productos similares usando descripción
        similar_products = []
        
        # Usar embeddings si están disponibles
        if analysis["embedding"]:
            # Por ahora, usar búsqueda por descripción de texto
            # En el futuro, se pueden guardar embeddings de productos
            pass
        
        # Búsqueda por similitud de texto usando RAG
        search_query = f"Buscar productos similares a: {image_description}"
        
        # Usar IA para recomendar productos basados en la descripción
        products_list = "\n".join([f"- ID:{p.id} | {p.title} | {p.description}" for p in products])
        
        ai_response = await ai_service.generate_response(
            prompt=f"""TAREA: Analizar imagen y recomendar productos similares.

DESCRIPCIÓN DE LA IMAGEN: "{image_description}"

PRODUCTOS DISPONIBLES:
{products_list}

INSTRUCCIONES:
1. Identifica qué tipo de producto se ve en la imagen (camisa, pantalón, zapatos, etc.)
2. Busca en la lista SOLO productos del mismo tipo o muy similares
3. Si NO HAY productos similares, responde "NO_MATCH"
4. Si SÍ HAY productos similares, responde SOLO los IDs separados por comas
5. Máximo 3 productos más relevantes

FORMATO DE RESPUESTA: 
- Si hay match: "1,3,5" (solo IDs)
- Si no hay match: "NO_MATCH"

RESPUESTA:"""
        )
        
        # Filtrar productos mencionados por la IA
        recommended_products = []
        
        # Obtener texto de respuesta (manejar diferentes tipos de respuesta)
        ai_text = ""
        if hasattr(ai_response, 'response'):
            ai_text = ai_response.response
        elif hasattr(ai_response, 'text'):
            ai_text = ai_response.text
        elif isinstance(ai_response, dict):
            ai_text = ai_response.get('response', ai_response.get('text', ''))
        elif isinstance(ai_response, str):
            ai_text = ai_response
        
        print(f"Respuesta de IA: {ai_text}")
        
        # Parsear IDs recomendados por la IA
        if "NO_MATCH" not in ai_text:
            # Extraer IDs de la respuesta
            import re
            ids_found = re.findall(r'\b\d+\b', ai_text)
            
            if ids_found:
                # Convertir a enteros
                product_ids = [int(id_str) for id_str in ids_found[:3]]  # Máximo 3
                
                # Obtener productos por ID
                for pid in product_ids:
                    product = db.get(models.Product, pid)
                    if product and product.active:
                        recommended_products.append({
                            "id": product.id,
                            "title": product.title,
                            "description": product.description,
                            "price": float(product.price),
                            "image_url": product.image_url,
                            "similarity_score": 0.9
                        })
        
        # Si no encontró productos por ID, buscar por coincidencia de palabras clave
        if not recommended_products:
            # Mapeo de categorías de ropa en inglés a español
            clothing_types = {
                "jeans": ["pantalon", "jean", "pants"],
                "pants": ["pantalon", "pants"],
                "shirt": ["camisa", "playera", "polo"],
                "shoes": ["zapato", "zapatos", "calzado", "botas"],
                "boots": ["bota", "botas"],
                "dress": ["vestido"],
                "skirt": ["falda"],
                "jacket": ["chaqueta", "chamarra"],
                "hat": ["gorro", "sombrero"],
                "t-shirt": ["camiseta", "playera"]
            }
            
            # Identificar tipo de producto en la imagen
            desc_lower = image_description.lower()
            product_type_found = None
            
            for eng_type, spanish_equivalents in clothing_types.items():
                if eng_type in desc_lower:
                    product_type_found = spanish_equivalents
                    break
            
            # Buscar productos del mismo tipo
            for product in products:
                product_text = f"{product.title} {product.description}".lower()
                
                score = 0
                
                # Si encontramos el tipo, dar prioridad a productos del mismo tipo
                if product_type_found:
                    for type_word in product_type_found:
                        if type_word in product_text:
                            score += 0.8  # Alto score por tipo coincidente
                
                # Buscar coincidencias de palabras clave
                keywords = [w for w in desc_lower.split() if len(w) > 3]
                for keyword in keywords:
                    if keyword in product_text:
                        score += 0.2
                
                # Solo agregar si hay match significativo
                if score >= 0.5:
                    recommended_products.append({
                        "id": product.id,
                        "title": product.title,
                        "description": product.description,
                        "price": float(product.price),
                        "image_url": product.image_url,
                        "similarity_score": score
                    })
            
            # Ordenar por score descendente
            recommended_products.sort(key=lambda x: x["similarity_score"], reverse=True)
            recommended_products = recommended_products[:3]  # Solo top 3
        
        # Si aún no hay productos, informar que no hay match
        if not recommended_products:
            ai_text = f"No encontré productos similares a '{image_description}' en nuestro catálogo actual. ¿Te gustaría ver todos nuestros productos disponibles?"
        
        # Generar mensaje personalizado
        if recommended_products:
            product_names = ", ".join([p["title"] for p in recommended_products[:3]])
            final_message = f"📸 He analizado la imagen: **{image_description}**\n\n✨ Encontré {len(recommended_products)} producto(s) similar(es): {product_names}"
        else:
            final_message = f"📸 Imagen analizada: **{image_description}**\n\n😔 No encontré productos exactamente iguales en nuestro catálogo, pero puedo ayudarte a buscar algo similar. ¿Qué tipo de producto buscas?"
        
        return {
            "image_analysis": {
                "description": image_description,
                "features": analysis["features"]
            },
            "similar_products": recommended_products,
            "ai_recommendation": final_message,
            "total_found": len(recommended_products)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en búsqueda por imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/describe-image")
async def describe_product_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Obtener descripción detallada de un producto en una imagen"""
    try:
        # Leer imagen
        image_data = await file.read()
        
        # Generar descripción detallada
        description = huggingface_image_service.describe_product_from_image(image_data)
        
        return {
            "description": description,
            "filename": file.filename,
            "success": True
        }
        
    except Exception as e:
        print(f"Error describiendo imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# ==================== ENDPOINTS PARA EL FRONTEND ====================

@image_search_router.post("/search")
async def search_by_image_frontend(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Endpoint para el frontend - buscar productos por imagen"""
    try:
        # Leer imagen
        image_data = await file.read()
        
        # Analizar imagen con Hugging Face
        print(f"Analizando imagen desde frontend: {file.filename}")
        analysis = huggingface_image_service.analyze_image(image_data)
        
        # Si el análisis falla, usar análisis básico
        if not analysis.get("success", False):
            print("⚠️ Análisis falló, usando análisis básico")
            analysis = {
                "success": True,
                "description": "Imagen procesada correctamente",
                "features": ["imagen", "producto"],
                "embedding": []
            }
        
        # Obtener descripción de la imagen
        image_description = analysis["description"]
        print(f"Descripcion generada: {image_description}")
        
        # Obtener todos los productos
        products = db.query(models.Product).filter(models.Product.active == True).all()
        
        # Buscar productos similares usando descripción
        similar_products = []
        
        # Búsqueda por similitud de texto usando RAG
        search_query = f"Buscar productos similares a: {image_description}"
        
        # Usar IA para recomendar productos basados en la descripción
        products_list = "\n".join([f"- ID:{p.id} | {p.title} | {p.description}" for p in products])
        
        ai_response = await ai_service.generate_response(
            prompt=f"""TAREA: Analizar imagen y recomendar productos similares.

DESCRIPCIÓN DE LA IMAGEN: "{image_description}"

PRODUCTOS DISPONIBLES:
{products_list}

INSTRUCCIONES:
1. Identifica qué tipo de producto se ve en la imagen (camisa, pantalón, zapatos, etc.)
2. Busca en la lista SOLO productos del mismo tipo o muy similares
3. Si NO HAY productos similares, responde "NO_MATCH"
4. Si SÍ HAY productos similares, responde SOLO los IDs separados por comas
5. Máximo 3 productos más relevantes

FORMATO DE RESPUESTA: 
- Si hay match: "1,3,5" (solo IDs)
- Si no hay match: "NO_MATCH"

RESPUESTA:"""
        )
        
        # Filtrar productos mencionados por la IA
        recommended_products = []
        
        # Obtener texto de respuesta (manejar diferentes tipos de respuesta)
        ai_text = ""
        if hasattr(ai_response, 'response'):
            ai_text = ai_response.response
        elif hasattr(ai_response, 'text'):
            ai_text = ai_response.text
        elif isinstance(ai_response, dict):
            ai_text = ai_response.get('response', ai_response.get('text', ''))
        elif isinstance(ai_response, str):
            ai_text = ai_response
        
        print(f"Respuesta de IA: {ai_text}")
        
        # Parsear IDs recomendados por la IA
        if "NO_MATCH" not in ai_text:
            # Extraer IDs de la respuesta
            import re
            ids_found = re.findall(r'\b\d+\b', ai_text)
            
            if ids_found:
                # Convertir a enteros
                product_ids = [int(id_str) for id_str in ids_found[:3]]  # Máximo 3
                
                # Obtener productos por ID
                for pid in product_ids:
                    product = db.get(models.Product, pid)
                    if product and product.active:
                        recommended_products.append({
                            "id": product.id,
                            "title": product.title,
                            "description": product.description,
                            "price": float(product.price),
                            "image_url": product.image_url,
                            "similarity_score": 0.9
                        })
        
        # Si no encontró productos por ID, buscar por coincidencia de palabras clave
        if not recommended_products:
            # Mapeo de categorías de ropa en inglés a español
            clothing_types = {
                "jeans": ["pantalon", "jean", "pants"],
                "pants": ["pantalon", "pants"],
                "shirt": ["camisa", "playera", "polo"],
                "shoes": ["zapato", "zapatos", "calzado", "botas"],
                "boots": ["bota", "botas"],
                "dress": ["vestido"],
                "skirt": ["falda"],
                "jacket": ["chaqueta", "chamarra"],
                "hat": ["gorro", "sombrero"],
                "t-shirt": ["camiseta", "playera"]
            }
            
            # Identificar tipo de producto en la imagen
            desc_lower = image_description.lower()
            product_type_found = None
            
            for eng_type, spanish_equivalents in clothing_types.items():
                if eng_type in desc_lower:
                    product_type_found = spanish_equivalents
                    break
            
            # Buscar productos del mismo tipo
            for product in products:
                product_text = f"{product.title} {product.description}".lower()
                
                score = 0
                
                # Si encontramos el tipo, dar prioridad a productos del mismo tipo
                if product_type_found:
                    for type_word in product_type_found:
                        if type_word in product_text:
                            score += 0.8  # Alto score por tipo coincidente
                
                # Buscar coincidencias de palabras clave
                keywords = [w for w in desc_lower.split() if len(w) > 3]
                for keyword in keywords:
                    if keyword in product_text:
                        score += 0.2
                
                # Solo agregar si hay match significativo
                if score >= 0.5:
                    recommended_products.append({
                        "id": product.id,
                        "title": product.title,
                        "description": product.description,
                        "price": float(product.price),
                        "image_url": product.image_url,
                        "similarity_score": score
                    })
            
            # Ordenar por score descendente
            recommended_products.sort(key=lambda x: x["similarity_score"], reverse=True)
            recommended_products = recommended_products[:3]  # Solo top 3
        
        # Generar mensaje personalizado
        if recommended_products:
            product_names = ", ".join([p["title"] for p in recommended_products[:3]])
            final_message = f"📸 He analizado la imagen: **{image_description}**\n\n✨ Encontré {len(recommended_products)} producto(s) similar(es): {product_names}"
        else:
            final_message = f"📸 Imagen analizada: **{image_description}**\n\n😔 No encontré productos exactamente iguales en nuestro catálogo, pero puedo ayudarte a buscar algo similar. ¿Qué tipo de producto buscas?"
        
        return {
            "success": True,
            "image_analysis": {
                "description": image_description,
                "features": analysis["features"]
            },
            "similar_products": recommended_products,
            "ai_recommendation": final_message,
            "total_found": len(recommended_products)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en búsqueda por imagen desde frontend: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


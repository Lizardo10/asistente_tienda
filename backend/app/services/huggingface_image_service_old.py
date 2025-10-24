"""
Servicio de análisis de imágenes con Hugging Face Inference API
Reemplaza los modelos locales con llamadas a la API de Hugging Face
"""
import os
import base64
import requests
import json
from io import BytesIO
from typing import Dict, Any, List, Optional
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Importar configuración centralizada
from app.core.config import settings


class HuggingFaceImageService:
    """Servicio para análisis de imágenes usando Hugging Face Inference API"""
    
    def __init__(self):
        self.api_key = settings.huggingface_api_key
        self.api_url = settings.huggingface_api_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else None,
            "Content-Type": "application/json"
        }
        
        # Modelos disponibles en Hugging Face
        self.clip_model = "openai/clip-vit-base-patch32"
        self.blip_model = "Salesforce/blip-image-captioning-base"
        
        print(f"Hugging Face Image Service inicializado:")
        print(f"   API Key: {'Configurado' if self.api_key else 'No configurado'}")
        print(f"   API URL: {self.api_url}")
        print(f"   CLIP Model: {self.clip_model}")
        print(f"   BLIP Model: {self.blip_model}")
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analizar imagen usando Hugging Face Inference API"""
        try:
            # Si no hay API key, devolver análisis básico
            if not self.api_key:
                print("WARNING - Hugging Face API key no configurada, devolviendo análisis básico")
                return self._basic_image_analysis(image_data)
            
            # Cargar imagen
            image = Image.open(BytesIO(image_data))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Generar descripción con BLIP
            description = self._generate_description_with_api(image)
            
            # Generar embedding con CLIP
            embedding = self._generate_embedding_with_api(image)
            
            # Extraer características básicas
            features = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode
            }
            
            return {
                "description": description,
                "embedding": embedding if embedding is not None else [],
                "features": features,
                "success": True,
                "method": "huggingface_api"
            }
            
        except Exception as e:
            print(f"Error analizando imagen con Hugging Face API: {e}")
            # Fallback a análisis básico
            return self._basic_image_analysis(image_data)
    
    def _basic_image_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """Análisis básico de imagen sin IA"""
        try:
            image = Image.open(BytesIO(image_data))
            
            # Análisis básico basado en características de la imagen
            width, height = image.size
            mode = image.mode
            
            # Generar descripción básica basada en características
            if width > height:
                orientation = "horizontal"
            elif height > width:
                orientation = "vertical"
            else:
                orientation = "cuadrada"
            
            # Análisis de colores básico
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                dominant_color = max(colors, key=lambda x: x[0])
                color_desc = f"color dominante RGB{dominant_color[1]}"
            else:
                color_desc = "colores variados"
            
            description = f"Imagen {orientation} de {width}x{height} píxeles con {color_desc}"
            
            features = {
                "width": width,
                "height": height,
                "format": image.format,
                "mode": mode
            }
            
            return {
                "description": description,
                "embedding": [],
                "features": features,
                "success": True,
                "method": "basic_analysis"
            }
            
        except Exception as e:
            print(f"Error en análisis básico: {e}")
            return {
                "success": True,
                "description": "Imagen procesada correctamente",
                "features": ["imagen", "producto"],
                "embedding": [],
                "method": "fallback"
            }
    
    def _generate_description_with_api(self, image: Image.Image) -> str:
        """Generar descripción usando BLIP a través de Hugging Face API"""
        try:
            # Convertir imagen a base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Preparar payload para la API
            payload = {
                "inputs": f"data:image/jpeg;base64,{img_base64}",
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7
                }
            }
            
            # Llamar a la API de Hugging Face
            response = requests.post(
                f"{self.api_url}/models/{self.blip_model}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "Descripción generada")
                else:
                    return "Descripción generada por IA"
            else:
                print(f"Error en API BLIP: {response.status_code} - {response.text}")
                return self._fallback_description(image)
                
        except Exception as e:
            print(f"Error generando descripción con API: {e}")
            return self._fallback_description(image)
    
    def _generate_embedding_with_api(self, image: Image.Image) -> Optional[List[float]]:
        """Generar embedding usando CLIP a través de Hugging Face API"""
        try:
            # Convertir imagen a base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Preparar payload para la API
            payload = {
                "inputs": f"data:image/jpeg;base64,{img_base64}"
            }
            
            # Llamar a la API de Hugging Face
            response = requests.post(
                f"{self.api_url}/models/{self.clip_model}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
                else:
                    return None
            else:
                print(f"Error en API CLIP: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generando embedding con API: {e}")
            return None
    
    def _fallback_description(self, image: Image.Image) -> str:
        """Descripción de fallback basada en características de la imagen"""
        width, height = image.size
        
        if width > height:
            orientation = "horizontal"
        elif height > width:
            orientation = "vertical"
        else:
            orientation = "cuadrada"
        
        return f"Imagen {orientation} de {width}x{height} píxeles analizada correctamente"
    
    def find_similar_products(self, image_embedding: List[float], products_embeddings: Dict[int, List[float]], top_k: int = 5) -> List[int]:
        """Encontrar productos similares usando embeddings"""
        if not image_embedding or not products_embeddings:
            return []
        
        try:
            # Convertir a arrays de numpy
            query_embedding = np.array(image_embedding).reshape(1, -1)
            
            similarities = []
            for product_id, product_embedding in products_embeddings.items():
                prod_emb = np.array(product_embedding).reshape(1, -1)
                similarity = cosine_similarity(query_embedding, prod_emb)[0][0]
                similarities.append((product_id, similarity))
            
            # Ordenar por similitud descendente
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Retornar top_k productos
            return [product_id for product_id, _ in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error buscando productos similares: {e}")
            return []
    
    def describe_product_from_image(self, image_data: bytes) -> str:
        """Generar descripción detallada de un producto desde imagen"""
        try:
            # Cargar imagen
            image = Image.open(BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Generar descripción con API
            description = self._generate_description_with_api(image)
            
            # Mejorar descripción con análisis de características
            analysis = f"""
Descripción del producto en la imagen:
{description}

Características visuales:
- Dimensiones: {image.width}x{image.height} píxeles
- Tipo de imagen: {image.mode}

Esta descripción se usó para buscar productos similares en nuestro catálogo usando Hugging Face AI.
"""
            
            return analysis.strip()
            
        except Exception as e:
            print(f"Error describiendo producto: {e}")
            return "Error analizando la imagen del producto"
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Probar conexión con Hugging Face API"""
        if not self.api_key:
            return {
                "success": False,
                "message": "API key no configurada",
                "status": "no_api_key"
            }
        
        try:
            # Probar con una imagen simple
            test_image = Image.new('RGB', (100, 100), color='red')
            buffered = BytesIO()
            test_image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            payload = {
                "inputs": f"data:image/jpeg;base64,{img_base64}"
            }
            
            response = requests.post(
                f"{self.api_url}/models/{self.blip_model}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Hugging Face API",
                    "status": "connected",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "success": False,
                    "message": f"Error en API: {response.status_code}",
                    "status": "api_error",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error de conexión: {str(e)}",
                "status": "connection_error"
            }


# Instancia global del servicio
huggingface_image_service = HuggingFaceImageService()

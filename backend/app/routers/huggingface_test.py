"""
Router para probar la integración con Hugging Face API oficial
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Dict, Any
from app.services.huggingface_image_service import huggingface_image_service
from app.core.config import settings
import base64
from io import BytesIO
from PIL import Image

router = APIRouter(prefix="/huggingface", tags=["Hugging Face"])


@router.get("/test-connection")
async def test_huggingface_connection() -> Dict[str, Any]:
    """Probar conexión con Hugging Face API oficial"""
    try:
        result = huggingface_image_service.test_api_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error probando conexión: {str(e)}")


@router.get("/status")
async def get_huggingface_status() -> Dict[str, Any]:
    """Obtener estado del servicio de Hugging Face"""
    return {
        "service": "Hugging Face Image Service (API Oficial)",
        "api_key_configured": bool(huggingface_image_service.api_key),
        "api_url": huggingface_image_service.api_url,
        "clip_model": huggingface_image_service.clip_model,
        "blip_model": huggingface_image_service.blip_model,
        "status": "ready" if huggingface_image_service.api_key else "API Key missing"
    }


@router.post("/test-image-analysis")
async def test_image_analysis_endpoint(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Endpoint de prueba para analizar una imagen subida usando Hugging Face API oficial"""
    image_data = await file.read()
    try:
        analysis_result = huggingface_image_service.analyze_image(image_data)
        return {
            "status": "success",
            "message": "Análisis de imagen completado con Hugging Face API oficial.",
            "analysis": analysis_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el análisis de imagen: {str(e)}")

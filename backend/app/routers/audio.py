"""
Router para procesamiento de audio con IA
Incluye transcripción de voz usando OpenAI Whisper
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import base64
import logging
from pydantic import BaseModel
from app.services.audio_service import audio_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["Audio Processing"])

class AudioTranscriptionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    filename: str = "audio.wav"
    language: str = "es"
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "dGVzdA==",
                "filename": "audio.wav",
                "language": "es"
            }
        }

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form(default="es")
):
    """
    Transcribir audio a texto usando OpenAI Whisper
    
    Args:
        audio_file: Archivo de audio
        language: Idioma (es, en, etc.)
        
    Returns:
        Texto transcrito
    """
    try:
        logger.info(f"🎤 Recibiendo archivo de audio: {audio_file.filename}")
        
        # Verificar formato soportado
        if not audio_service.is_supported_format(audio_file.filename or "audio.wav"):
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Formatos válidos: {audio_service.supported_formats}"
            )
        
        # Leer datos del archivo
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Archivo de audio vacío")
        
        # Transcribir
        transcript = await audio_service.transcribe_audio(
            audio_data, 
            audio_file.filename or "audio.wav"
        )
        
        if transcript is None:
            raise HTTPException(status_code=500, detail="Error procesando el audio")
        
        logger.info(f"✅ Transcripción exitosa: {len(transcript)} caracteres")
        
        return {
            "success": True,
            "transcript": transcript,
            "language": language,
            "filename": audio_file.filename,
            "length": len(transcript)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en transcripción: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/transcribe-base64")
async def transcribe_base64_audio(request: AudioTranscriptionRequest):
    """
    Transcribir audio desde base64
    
    Args:
        request: Datos del audio en base64
        
    Returns:
        Texto transcrito
    """
    try:
        logger.info(f"🎤 Recibiendo audio base64: {request.filename}")
        
        # Verificar formato soportado
        if not audio_service.is_supported_format(request.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Formatos válidos: {audio_service.supported_formats}"
            )
        
        # Transcribir
        transcript = await audio_service.transcribe_base64_audio(request.audio_data, request.filename)
        
        if transcript is None:
            logger.error("❌ Transcripción falló - OpenAI no disponible o error en procesamiento")
            raise HTTPException(
                status_code=503, 
                detail="Servicio de transcripción no disponible. Verifique la configuración de OpenAI."
            )
        
        logger.info(f"✅ Transcripción exitosa: {len(transcript)} caracteres")
        
        return {
            "success": True,
            "transcript": transcript,
            "language": request.language,
            "filename": request.filename,
            "length": len(transcript)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en transcripción base64: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats():
    """Obtener formatos de audio soportados"""
    return {
        "supported_formats": audio_service.supported_formats,
        "max_file_size": "25MB",  # Límite de OpenAI Whisper
        "languages": ["es", "en", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
    }

# aws_rekognition_integration.py
import boto3
import base64
from typing import List, Dict, Optional
from PIL import Image
import io

class AWSRekognitionService:
    def __init__(self):
        self.rekognition = boto3.client('rekognition', region_name='us-east-1')
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.bucket_name = 'asistente-tienda-imagenes'
    
    def analyze_product_image(self, image_bytes: bytes) -> Dict:
        """Analiza imagen de producto y extrae características"""
        try:
            # Detectar etiquetas (categorías de producto)
            labels_response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=10,
                MinConfidence=75
            )
            
            # Detectar texto (precios, nombres, códigos)
            text_response = self.rekognition.detect_text(
                Image={'Bytes': image_bytes}
            )
            
            # Detectar caras (si es producto con personas)
            faces_response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            
            return {
                'labels': labels_response['Labels'],
                'text_detections': text_response['TextDetections'],
                'faces': faces_response['FaceDetails'],
                'analysis_type': 'product_image'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_support_image(self, image_bytes: bytes) -> Dict:
        """Analiza imagen de soporte técnico"""
        try:
            # Detectar objetos técnicos
            labels_response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=15,
                MinConfidence=70
            )
            
            # Detectar texto (códigos de error, manuales)
            text_response = self.rekognition.detect_text(
                Image={'Bytes': image_bytes}
            )
            
            return {
                'labels': labels_response['Labels'],
                'text_detections': text_response['TextDetections'],
                'analysis_type': 'support_image'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def upload_to_s3(self, image_bytes: bytes, filename: str) -> str:
        """Sube imagen a S3 y retorna URL"""
        try:
            key = f"images/{filename}"
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except Exception as e:
            raise Exception(f"Error uploading to S3: {str(e)}")

# Integración con FastAPI
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

app = FastAPI()
rekognition_service = AWSRekognitionService()

class ImageAnalysisResponse(BaseModel):
    analysis: Dict
    s3_url: Optional[str] = None
    success: bool

@app.post("/analyze-product-image", response_model=ImageAnalysisResponse)
async def analyze_product_image(file: UploadFile = File(...)):
    try:
        # Leer imagen
        image_bytes = await file.read()
        
        # Analizar con Rekognition
        analysis = rekognition_service.analyze_product_image(image_bytes)
        
        # Subir a S3
        s3_url = rekognition_service.upload_to_s3(image_bytes, file.filename)
        
        return ImageAnalysisResponse(
            analysis=analysis,
            s3_url=s3_url,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-support-image", response_model=ImageAnalysisResponse)
async def analyze_support_image(file: UploadFile = File(...)):
    try:
        # Leer imagen
        image_bytes = await file.read()
        
        # Analizar con Rekognition
        analysis = rekognition_service.analyze_support_image(image_bytes)
        
        # Subir a S3
        s3_url = rekognition_service.upload_to_s3(image_bytes, file.filename)
        
        return ImageAnalysisResponse(
            analysis=analysis,
            s3_url=s3_url,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))










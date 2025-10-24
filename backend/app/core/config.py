"""
Configuración centralizada de la aplicación usando Pydantic Settings
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # JWT
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=120, env="JWT_EXPIRE_MINUTES")
    
    # CORS
    allowed_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
    
    @field_validator('allowed_origins', mode='after')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Media
    media_dir: str = Field(default="media", env="MEDIA_DIR")
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Hugging Face
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    huggingface_api_url: str = Field(default="https://api-inference.huggingface.co", env="HUGGINGFACE_API_URL")
    
    # Email configuration
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    email_user: Optional[str] = Field(default=None, env="EMAIL_USER")
    email_password: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    from_email: Optional[str] = Field(default=None, env="FROM_EMAIL")
    app_name: str = Field(default="Tu Tienda", env="APP_NAME")
    frontend_url: str = Field(default="http://localhost:5174", env="FRONTEND_URL")
    
    # Brevo/SendInBlue configuration
    brevo_api_key: Optional[str] = Field(default=None, env="BREVO_API_KEY")
    
    # RAG
    rag_index_path: str = Field(default="rag_index", env="RAG_INDEX_PATH")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # PayPal Configuration
    paypal_client_id: Optional[str] = Field(default=None, env="PAYPAL_CLIENT_ID")
    paypal_client_secret: Optional[str] = Field(default=None, env="PAYPAL_CLIENT_SECRET")
    paypal_mode: str = Field(default="sandbox", env="PAYPAL_MODE")  # sandbox or live
    paypal_base_url: str = Field(default="https://api.sandbox.paypal.com", env="PAYPAL_BASE_URL")
    paypal_return_url: str = Field(default="http://localhost:5173/checkout/success", env="PAYPAL_RETURN_URL")
    paypal_cancel_url: str = Field(default="http://localhost:5173/checkout/cancel", env="PAYPAL_CANCEL_URL")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()

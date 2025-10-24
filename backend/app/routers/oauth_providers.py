# backend/app/routers/oauth_providers.py
"""
Proveedores OAuth 2.0 para autenticación social
Google, Facebook, GitHub, Microsoft
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
import httpx
from typing import Dict, Any
import os

router = APIRouter(prefix="/oauth", tags=["oauth"])

# Configuración de proveedores
OAUTH_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo",
        "scope": "openid email profile"
    },
    "facebook": {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "user_info_url": "https://graph.facebook.com/me",
        "scope": "email"
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_info_url": "https://api.github.com/user",
        "scope": "user:email"
    }
}

@router.get("/{provider}/login")
async def oauth_login(provider: str):
    """Iniciar proceso de login OAuth"""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Proveedor no soportado")
    
    config = OAUTH_PROVIDERS[provider]
    redirect_uri = f"http://localhost:8000/oauth/{provider}/callback"
    
    auth_url = (
        f"{config['auth_url']}?"
        f"client_id={config['client_id']}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={config['scope']}&"
        f"response_type=code"
    )
    
    return RedirectResponse(url=auth_url)

@router.get("/{provider}/callback")
async def oauth_callback(provider: str, code: str):
    """Callback de OAuth"""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Proveedor no soportado")
    
    config = OAUTH_PROVIDERS[provider]
    
    # Intercambiar código por token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            config["token_url"],
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "grant_type": "authorization_code"
            }
        )
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Error obteniendo token")
        
        # Obtener información del usuario
        user_response = await client.get(
            config["user_info_url"],
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        user_data = user_response.json()
        
        # Procesar datos según el proveedor
        if provider == "google":
            return await process_google_user(user_data)
        elif provider == "facebook":
            return await process_facebook_user(user_data)
        elif provider == "github":
            return await process_github_user(user_data)

async def process_google_user(user_data: Dict[str, Any]):
    """Procesar datos de usuario de Google"""
    return {
        "provider": "google",
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": user_data.get("picture"),
        "verified": user_data.get("verified_email", False)
    }

async def process_facebook_user(user_data: Dict[str, Any]):
    """Procesar datos de usuario de Facebook"""
    return {
        "provider": "facebook",
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": f"https://graph.facebook.com/{user_data.get('id')}/picture"
    }

async def process_github_user(user_data: Dict[str, Any]):
    """Procesar datos de usuario de GitHub"""
    return {
        "provider": "github",
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "username": user_data.get("login"),
        "picture": user_data.get("avatar_url")
    }

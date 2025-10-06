from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .db import get_db
from . import models
from .auth_utils import decode_token

def _get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.split(" ", 1)[1].strip()

def get_current_user(authorization: Optional[str] = Header(None, alias="Authorization"),
                     db: Session = Depends(get_db)) -> models.User:
    token = _get_bearer_token(authorization)
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).get(int(sub)) if sub else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user

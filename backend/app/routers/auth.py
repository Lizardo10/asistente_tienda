from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database.connection import get_db
from .. import models
from .. import schemas as app_schemas
from ..auth_utils import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=app_schemas.Token, status_code=201)
def register(data: app_schemas.RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = models.User(
        email=email,
        full_name=(data.full_name or "").strip(),
        password_hash=hash_password(data.password),
        active=True,
        mfa_enabled=False
    )
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}

@router.post("/login", response_model=app_schemas.Token)
def login(data: app_schemas.LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}

@router.post("/password-reset-request")
def password_reset_request(payload: app_schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"ok": True}
    from datetime import datetime, timedelta
    from jose import jwt
    from ..auth_utils import JWT_SECRET, ALGORITHM
    exp = datetime.utcnow() + timedelta(minutes=15)
    token = jwt.encode({"sub": str(user.id), "type": "reset", "exp": exp}, JWT_SECRET, algorithm=ALGORITHM)
    return {"ok": True, "reset_token": token}

@router.post("/password-reset-confirm")
def password_reset_confirm(payload: app_schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    data = decode_token(payload.token)
    if data.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid reset token")
    user = db.query(models.User).get(int(data["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="models.User not found")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"ok": True}
from ..security import get_current_user

@router.get("/me")
def me(authorization: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)):
    from ..auth_utils import decode_token
    
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).get(int(sub)) if sub else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "role": user.role,
        "balance": user.balance,
        "created_at": user.created_at
    }

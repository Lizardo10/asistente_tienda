from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..auth_utils import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.Token, status_code=201)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = models.User(
        email=email,
        full_name=(data.full_name or "").strip(),
        hashed_password=hash_password(data.password),
    )
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}

@router.post("/password-reset-request")
def password_reset_request(payload: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
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
def password_reset_confirm(payload: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    data = decode_token(payload.token)
    if data.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid reset token")
    user = db.query(models.User).get(int(data["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"ok": True}
from ..security import get_current_user

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user

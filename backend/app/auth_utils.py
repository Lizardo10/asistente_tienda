# backend/app/auth_utils.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-super-secret")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

# ✅ Hash robusto y portable en Windows, sin límite de 72 bytes
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
print("AUTH_UTILS_LOADED schemes ->", pwd_context.schemes())  # debe mostrar ('pbkdf2_sha256',)

def hash_password(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)
    return pwd_context.hash(password.strip())

def verify_password(plain: str, hashed: str) -> bool:
    if not isinstance(plain, str):
        plain = str(plain)
    return pwd_context.verify(plain.strip(), hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

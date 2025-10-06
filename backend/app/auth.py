from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

# Configuración JWT / bcrypt
ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-super-secret")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _normalize_pass(p: str) -> str:
    """
    Normaliza la contraseña (string, trim) y trunca a 72 bytes (límite bcrypt).
    """
    if not isinstance(p, str):
        p = str(p)
    p = p.strip()
    b = p.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
    return b.decode("utf-8", errors="ignore")

def hash_password(password: str) -> str:
    return pwd_context.hash(_normalize_pass(password))

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_normalize_pass(plain), hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

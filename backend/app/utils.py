from fastapi import HTTPException, status

def raise_400(msg: str):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

def raise_401(msg: str = "Credenciales inválidas"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

def raise_404(msg: str = "No encontrado"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

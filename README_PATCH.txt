PARCHE UI + AUTH:
- Backend: bcrypt_sha256 para contraseñas (sin límite 72 bytes), endpoints de reset y dependencias JWT.
- Frontend: navbar + cards con Bootstrap, pantallas de Registro/Login/Reset.

Instalación (frontend):
  cd frontend
  npm i bootstrap dompurify
  npm run dev

Backend:
  cd backend
  .\.venv\Scripts\Activate.ps1
  uvicorn app.main:app --reload --port 8000

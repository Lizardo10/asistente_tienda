from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..services.openai_service import ask_openai
from ..services.rag_service import rag_answer

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message")
def post_message(data: schemas.ChatMessageIn, db: Session = Depends(get_db)):
    # Guarda mensaje usuario y genera respuesta simple (no WebSocket)
    msg = models.ChatMessage(chat_id=data.chat_id, sender="user", content=data.content)
    db.add(msg); db.commit(); db.refresh(msg)

    context = rag_answer(data.content)
    prompt = f"Contexto (opcional):\n{context}\n\nPregunta: {data.content}"
    answer = ask_openai(prompt)

    bot = models.ChatMessage(chat_id=data.chat_id, sender="bot", content=answer)
    db.add(bot); db.commit(); db.refresh(bot)
    return {"user": msg.id, "bot": bot.id}

@router.websocket("/ws/support")
async def ws_support(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    # Crear chat (anónimo) al conectar
    chat = models.Chat(status="open")
    db.add(chat); db.commit(); db.refresh(chat)
    await websocket.send_json({"type":"chat_opened", "chat_id": chat.id})

    try:
        while True:
            data = await websocket.receive_text()
            # guardar usuario
            m = models.ChatMessage(chat_id=chat.id, sender="user", content=data)
            db.add(m); db.commit(); db.refresh(m)

            context = rag_answer(data)
            prompt = f"Contexto (opcional):\n{context}\n\nPregunta: {data}"
            answer = ask_openai(prompt)

            # guardar bot
            b = models.ChatMessage(chat_id=chat.id, sender="bot", content=answer)
            db.add(b); db.commit(); db.refresh(b)

            await websocket.send_json({"type":"bot", "message": answer})
    except WebSocketDisconnect:
        chat.status = "closed"
        db.commit()
        return

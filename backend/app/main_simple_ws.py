from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Asistente Tienda - WebSocket Simple")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "WebSocket simple funcionando"}

@app.websocket("/ws/support")
async def websocket_support(websocket: WebSocket):
    """WebSocket simple para soporte"""
    await websocket.accept()
    
    try:
        # Enviar mensaje de bienvenida
        welcome_message = {
            "type": "chat_opened",
            "message": "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
        }
        await websocket.send_json(welcome_message)
        
        while True:
            data = await websocket.receive_text()
            print(f"Mensaje recibido: '{data}'")
            
            # Respuesta simple
            response = {
                "type": "bot",
                "message": f"Recibí tu mensaje: {data}",
                "timestamp": "2025-10-25T08:10:00Z"
            }
            await websocket.send_json(response)
            
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        await websocket.close(code=1011, reason="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)







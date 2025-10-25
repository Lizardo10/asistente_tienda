from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket conectado")
    await websocket.accept()
    print("WebSocket aceptado")
    
    try:
        await websocket.send_text("¡Hola! WebSocket funcionando")
        print("Mensaje enviado")
        
        while True:
            data = await websocket.receive_text()
            print(f"Mensaje recibido: {data}")
            await websocket.send_text(f"Echo: {data}")
            print(f"Echo enviado: {data}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)





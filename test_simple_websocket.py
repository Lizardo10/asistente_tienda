import asyncio
import websockets
import json

async def test_simple_websocket():
    uri = "ws://localhost:8000/ws/test"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("=== Conectado al WebSocket de prueba ===")
            
            # Recibir mensaje de bienvenida
            welcome = await websocket.recv()
            print(f"Mensaje de bienvenida: {welcome}")
            
            # Enviar mensaje de prueba
            test_message = "Hola WebSocket"
            print(f"\nEnviando: {test_message}")
            await websocket.send(test_message)
            
            # Recibir respuesta
            response = await websocket.recv()
            print(f"Respuesta: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_websocket())





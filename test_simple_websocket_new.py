import asyncio
import websockets

async def test_simple_websocket():
    uri = "ws://localhost:8000/ws/simple"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("=== Conectado al WebSocket SIMPLE ===")
            
            # Recibir mensaje de bienvenida
            welcome = await websocket.recv()
            print(f"Mensaje de bienvenida: {welcome}")
            
            # Enviar mensaje de prueba
            test_message = "Hola WebSocket simple"
            print(f"\nEnviando: {test_message}")
            await websocket.send(test_message)
            
            # Recibir respuesta
            response = await websocket.recv()
            print(f"Respuesta: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_websocket())





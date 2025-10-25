import asyncio
import websockets
import json

async def test_new_websocket():
    uri = "ws://localhost:8000/ws/support-new"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("=== Conectado al WebSocket NUEVO ===")
            
            # Recibir mensaje de bienvenida
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"Mensaje de bienvenida: {welcome_data['message']}")
            
            # Enviar mensaje de prueba
            test_message = "¿Qué camisetas tienes disponibles?"
            print(f"\nEnviando: {test_message}")
            await websocket.send(test_message)
            
            # Recibir respuesta
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"\nRespuesta del bot: {response_data['message']}")
            
            if 'recommendations' in response_data:
                print(f"\nRecomendaciones: {len(response_data['recommendations'])}")
                for rec in response_data['recommendations'][:3]:
                    print(f"- {rec['title']} (${rec['price']})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_websocket())





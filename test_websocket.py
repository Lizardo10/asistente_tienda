import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/support"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("=== Conectado al WebSocket ===")
            
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
            
            # Segundo mensaje de prueba
            test_message2 = "¿Cuál es la política de envíos?"
            print(f"\nEnviando: {test_message2}")
            await websocket.send(test_message2)
            
            # Recibir segunda respuesta
            response2 = await websocket.recv()
            response_data2 = json.loads(response2)
            print(f"\nRespuesta del bot: {response_data2['message']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())






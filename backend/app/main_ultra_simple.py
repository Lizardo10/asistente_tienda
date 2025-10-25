from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "WebSocket simple funcionando"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)







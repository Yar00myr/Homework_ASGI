import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int:[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if chat_id not in self.active_connections.keys():
            self.active_connections[chat_id] = []
        if len(self.active_connections.get(chat_id)) < 2:
            self.active_connections[chat_id].append(websocket)
        print(self.active_connections)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        if chat_id in self.active_connections:
            self.active_connections.get(chat_id).remove(websocket)
        print(self.active_connections)

    async def broadcast(self, chat_id: int, message: str, websocket: WebSocket):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                if connection != websocket:
                    await connection.send_text(message)

manager = ConnectionManager()




@app.websocket("/ws/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: int):
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            if message:
                await manager.broadcast(chat_id, message, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
from fastapi import WebSocket
from typing import Any
from backend.utils.logger import get_logger

logger = get_logger("ws_manager")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def send(self, client_id: str, data: dict):
        ws = self.active_connections.get(client_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.error(f"Send to {client_id} failed: {e}")
                self.disconnect(client_id)

    async def broadcast(self, data: dict):
        disconnected = []
        for client_id, ws in self.active_connections.items():
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(client_id)
        for cid in disconnected:
            self.disconnect(cid)

    async def handle_message(self, client_id: str, data: dict):
        msg_type = data.get("type")
        if msg_type == "ping":
            await self.send(client_id, {"type": "pong"})
        elif msg_type == "subscribe":
            logger.info(f"{client_id} subscribed to {data.get('channel')}")
        elif msg_type == "unsubscribe":
            logger.info(f"{client_id} unsubscribed from {data.get('channel')}")

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()

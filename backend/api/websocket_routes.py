from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from backend.websocket.manager import manager
from backend.utils.logger import get_logger

router = APIRouter()
logger = get_logger("ws_routes")


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    logger.info(f"WebSocket connected: {client_id}")
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(client_id, data)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        manager.disconnect(client_id)
        logger.error(f"WebSocket error {client_id}: {e}")

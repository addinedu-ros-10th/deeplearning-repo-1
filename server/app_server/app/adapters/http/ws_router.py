from fastapi import APIRouter, WebSocket, Query
from app.services.ws_notify import connection_manager


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, user_id: str = Query(...)):
    await connection_manager.connect(user_id, ws)
    try:
        while True:
            # optional ping/pong; ignore incoming
            await ws.receive_text()
    except Exception:
        pass
    finally:
        connection_manager.disconnect(user_id, ws)



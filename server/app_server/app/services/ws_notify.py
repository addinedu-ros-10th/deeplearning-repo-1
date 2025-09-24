from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.user_to_sockets: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.user_to_sockets.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        sockets = self.user_to_sockets.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self.user_to_sockets.pop(user_id, None)

    async def send_user(self, user_id: str, payload: dict) -> int:
        sockets = list(self.user_to_sockets.get(user_id, set()))
        success = 0
        for ws in sockets:
            try:
                await ws.send_json(payload)
                success += 1
            except Exception:
                self.disconnect(user_id, ws)
        return success


class WsNotifier:
    def __init__(self, manager: ConnectionManager) -> None:
        self.manager = manager

    async def notify(self, delivery: dict) -> int:
        # delivery: { user_id: UUID, payload: dict }
        user_id = str(delivery["user_id"]) if delivery.get("user_id") is not None else ""
        payload = delivery.get("payload") or {}
        return await self.manager.send_user(user_id, payload)


connection_manager = ConnectionManager()
ws_notifier = WsNotifier(connection_manager)



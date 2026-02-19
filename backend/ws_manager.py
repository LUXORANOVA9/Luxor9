from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, task_id: str):
        await ws.accept()
        self.connections.setdefault(task_id, []).append(ws)

    def disconnect(self, ws: WebSocket, task_id: str):
        if task_id in self.connections:
            self.connections[task_id] = [w for w in self.connections[task_id] if w != ws]

    async def broadcast_to_task(self, task_id: str, event: dict):
        if task_id not in self.connections:
            return
        msg = json.dumps(event, default=str)
        dead = []
        for ws in self.connections.get(task_id, []):
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, task_id)

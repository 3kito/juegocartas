class WebSocketManager:
    """Utility class to manage WebSocket connections for multiple players."""
    def __init__(self):
        self.connections = {}

    async def connect(self, player_id: int, ws):
        await ws.accept()
        self.connections[player_id] = ws

    def disconnect(self, player_id: int):
        self.connections.pop(player_id, None)

    def get(self, player_id: int):
        return self.connections.get(player_id)

    async def send_to(self, player_id: int, message: dict):
        ws = self.connections.get(player_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        disconnected = []
        for pid, ws in self.connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                # Client disconnected unexpectedly
                disconnected.append(pid)
        for pid in disconnected:
            self.disconnect(pid)

    def connected_players(self):
        return list(self.connections.keys())

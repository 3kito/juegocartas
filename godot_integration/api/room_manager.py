class Room:
    """Represents a game room with its own board and player list."""

    def __init__(self, room_id: str, max_players: int = 6):
        from src.game.board.hex_board import HexBoard

        self.room_id = room_id
        self.max_players = max_players
        self.players: list[int] = []
        self.board = HexBoard(radio=2)

    def add_player(self, player_id: int) -> bool:
        if player_id in self.players:
            return True
        if len(self.players) >= self.max_players:
            return False
        self.players.append(player_id)
        return True

    def remove_player(self, player_id: int) -> None:
        if player_id in self.players:
            self.players.remove(player_id)


class RoomManager:
    """Simple in-memory room management."""

    def __init__(self):
        self.rooms: dict[str, Room] = {}

    def get_room(self, room_id: str) -> Room:
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id)
        return self.rooms[room_id]

    def join_room(self, room_id: str, player_id: int) -> Room:
        room = self.get_room(room_id)
        room.add_player(player_id)
        return room

    def leave_room(self, room_id: str, player_id: int) -> None:
        room = self.rooms.get(room_id)
        if room:
            room.remove_player(player_id)
            if not room.players:
                # Remove empty room
                self.rooms.pop(room_id, None)

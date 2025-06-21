from typing import List, Set, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel

from src.game.board.hex_board import HexBoard
from src.game.board.hex_coordinate import HexCoordinate
from src.game.cards.base_card import BaseCard
from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego
from .websocket_manager import WebSocketManager

app = FastAPI(title="AutoBattler API")

board = HexBoard(radio=2)

manager = WebSocketManager()
players: Dict[int, Jugador] = {}
motor: MotorJuego | None = None


class Coordinate(BaseModel):
    q: int
    r: int


class CardPayload(BaseModel):
    nombre: str = "Carta"
    id: int | None = None
    stats: dict = {}


clients: Set[WebSocket] = set()


def serialize_player_board(jugador: Jugador) -> List[dict]:
    return [
        {
            "q": coord.q,
            "r": coord.r,
            "card": getattr(card, "nombre", None),
        }
        for coord, card in jugador.tablero.obtener_cartas_con_posiciones()
    ]


def get_game_state(player_id: int) -> dict:
    jugador = players.get(player_id)
    if not jugador:
        return {"type": "error", "detail": "player not found"}
    phase = motor.fase_actual if motor else "preparacion"
    time_remaining = 0.0
    if motor:
        if phase == "preparacion" and motor.controlador_preparacion:
            time_remaining = motor.controlador_preparacion.obtener_tiempo_restante()
        elif phase == "combate" and motor.controlador_enfrentamiento:
            time_remaining = motor.controlador_enfrentamiento.obtener_tiempo_restante_turno()
    return {
        "type": "game_state",
        "phase": phase,
        "time_remaining": time_remaining,
        "player_data": {
            "gold": jugador.oro,
            "level": jugador.nivel,
            "health": jugador.vida,
        },
        "board_state": serialize_player_board(jugador),
    }


def serialize_board() -> List[dict]:
    return [
        {"q": coord.q, "r": coord.r, "card": getattr(card, "nombre", None)}
        for coord, card in board.obtener_cartas_con_posiciones()
    ]


async def notify_board():
    payload = {
        "cartas": serialize_board(),
        "stats": board.obtener_estadisticas(),
    }
    for ws in list(clients):
        try:
            await ws.send_json(payload)
        except WebSocketDisconnect:
            clients.discard(ws)


async def handle_player_action(player: Jugador, data: dict):
    """Process a minimal subset of player actions."""
    action = data.get("action")
    if action == "gain_gold":
        amount = int(data.get("amount", 0))
        if amount > 0:
            player.ganar_oro(amount, razon="ws_action")
    elif action == "end_combat" and motor:
        motor.transicionar_a_fase_preparacion()


@app.get("/status")
def get_status():
    return {"status": "ok"}


@app.get("/board")
def get_board():
    return {"cartas": serialize_board(), "stats": board.obtener_estadisticas()}


@app.post("/board/place")
async def place_card(
    payload: CardPayload, coord: Coordinate, background_tasks: BackgroundTasks
):
    card = BaseCard(
        {
            "id": payload.id or 0,
            "nombre": payload.nombre,
            "stats": payload.stats,
        }
    )
    board.colocar_carta(HexCoordinate(coord.q, coord.r), card)
    background_tasks.add_task(notify_board)
    return {"status": "placed"}


@app.post("/board/move")
async def move_card(
    origin: Coordinate, dest: Coordinate, background_tasks: BackgroundTasks
):
    board.mover_carta(
        HexCoordinate(origin.q, origin.r),
        HexCoordinate(dest.q, dest.r),
    )
    background_tasks.add_task(notify_board)
    return {"status": "moved"}


@app.post("/board/remove")
async def remove_card(coord: Coordinate, background_tasks: BackgroundTasks):
    board.quitar_carta(HexCoordinate(coord.q, coord.r))
    background_tasks.add_task(notify_board)
    return {"status": "removed"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        await ws.send_json(
            {
                "cartas": serialize_board(),
                "stats": board.obtener_estadisticas(),
            }
        )
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.discard(ws)


@app.websocket("/ws/game/{player_id}")
async def websocket_game(ws: WebSocket, player_id: int):
    await manager.connect(player_id, ws)
    player = players.get(player_id)
    global motor
    if not player:
        player = Jugador(player_id, f"Jugador {player_id}")
        players[player_id] = player
    if motor is None:
        motor = MotorJuego(list(players.values()))
        motor.iniciar()
    try:
        await ws.send_json(get_game_state(player_id))
        while True:
            data = await ws.receive_json()
            if data.get("type") == "player_action":
                await handle_player_action(player, data)
                await manager.send_to(player_id, get_game_state(player_id))
            elif data.get("type") == "request_state":
                await manager.send_to(player_id, get_game_state(player_id))
    except WebSocketDisconnect:
        manager.disconnect(player_id)

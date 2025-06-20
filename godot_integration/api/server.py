from typing import List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel

from src.game.board.hex_board import HexBoard
from src.game.board.hex_coordinate import HexCoordinate
from src.game.cards.base_card import BaseCard

app = FastAPI(title="AutoBattler API")

board = HexBoard(radio=2)


class Coordinate(BaseModel):
    q: int
    r: int


class CardPayload(BaseModel):
    nombre: str = "Carta"
    id: int | None = None
    stats: dict = {}


clients: Set[WebSocket] = set()


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

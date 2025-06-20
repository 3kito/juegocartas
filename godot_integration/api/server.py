from fastapi import FastAPI
from src.game.board.hex_board import HexBoard

app = FastAPI(title="AutoBattler API")

board = HexBoard(radio=2)

@app.get("/status")
def get_status():
    return {"status": "ok"}

@app.get("/board")
def get_board():
    data = [
        {"q": coord.q, "r": coord.r, "card": getattr(card, "nombre", None)}
        for coord, card in board.obtener_cartas_con_posiciones()
    ]
    return {"cartas": data, "stats": board.obtener_estadisticas()}

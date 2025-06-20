from fastapi.testclient import TestClient

from godot_integration.api.server import app, board
from src.game.board.hex_coordinate import HexCoordinate

client = TestClient(app)


def test_status_endpoint():
    resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_place_and_move_card():
    board.limpiar_tablero()
    payload = {
        "nombre": "Test",
        "id": 1,
        "stats": {"vida": 5},
    }
    resp = client.post(
        "/board/place",
        json={"payload": payload, "coord": {"q": 0, "r": 0}},
    )
    assert resp.status_code == 200
    assert board.obtener_carta_en(HexCoordinate(0, 0)) is not None

    resp = client.post(
        "/board/move",
        json={
            "origin": {"q": 0, "r": 0},
            "dest": {"q": 1, "r": 0},
        },
    )
    assert resp.status_code == 200
    assert board.obtener_carta_en(HexCoordinate(1, 0)) is not None

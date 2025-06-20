# API Reference

The FastAPI server in `godot_integration/api/server.py` exposes the following endpoints:

- `GET /status` – basic health check.
- `GET /board` – returns board state with statistics.
- `POST /board/place` – place a card on the board.
- `POST /board/move` – move a card between coordinates.
- `POST /board/remove` – remove a card from a coordinate.
- `WebSocket /ws` – receive real time board updates.

Each coordinate is represented with `q` and `r` fields. Card creation accepts a `nombre` and optional `id` and `stats` dictionary.


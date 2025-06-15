# src/game/economia/entregador_oro.py
from src.utils.helpers import log_evento

ORO_POR_RONDA = 10  # Podés ajustar según lógica del juego

def entregar_oro_base(jugador):
    jugador.oro += ORO_POR_RONDA
    log_evento(f"💰 {jugador.nombre} recibe {ORO_POR_RONDA} de oro")

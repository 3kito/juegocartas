"""
SistemaSubastas - Gestión de subastas públicas por ronda durante la fase de preparación
"""

from typing import List, Dict, Optional
from src.game.cartas.manager_cartas import manager_cartas
from src.utils.helpers import log_evento


class SistemaSubastas:
    def __init__(self, jugadores: List, duracion_segundos: int = 15):
        self.jugadores = jugadores
        self.cartas_subastadas: Dict[int, dict] = {}  # carta_id: {"carta": Carta, "mejor_oferta": int, "jugador": Jugador}
        self.ofertas_por_jugador: Dict[int, List[int]] = {}  # jugador_id: [ids de cartas ofertadas]
        self.tiempo_restante = duracion_segundos

    # En src/game/tienda/sistema_subastas.py - método generar_subasta()
    def generar_subasta(self, cantidad: int = 3):
        self.cartas_subastadas.clear()
        log_evento(f"🏛️ Generando subasta con {cantidad} cartas:")

        for i in range(cantidad):
            cartas = manager_cartas.obtener_cartas_aleatorias_por_nivel(nivel_jugador=5, cantidad=1)
            if cartas:
                carta = cartas[0]
                self.cartas_subastadas[carta.id] = {"carta": carta, "mejor_oferta": 0, "jugador": None}
                log_evento(f"   🏛️ Carta {i + 1}: {carta.nombre} (ID: {carta.id}, Tier {carta.tier})")
            else:
                log_evento(f"   ⚠️ No se pudo generar carta {i + 1} para subasta")

    def ofertar(self, jugador, carta_id: int, monto: int) -> str:
        if carta_id not in self.cartas_subastadas:
            return "❌ Carta no disponible en subasta"

        entrada = self.cartas_subastadas[carta_id]
        if monto <= entrada["mejor_oferta"]:
            return "❌ Tu oferta debe superar la oferta actual"

        if not jugador.puede_gastar_oro(monto):
            return "❌ No tienes suficiente oro disponible"

        entrada["mejor_oferta"] = monto
        entrada["jugador"] = jugador
        self.ofertas_por_jugador.setdefault(jugador.id, []).append(carta_id)

        log_evento(f"💰 {jugador.nombre} oferta {monto} oro por {entrada['carta'].nombre}")
        return f"✅ Oferta aceptada por {entrada['carta'].nombre}"

    def resolver_subastas(self):
        for carta_id, entrada in self.cartas_subastadas.items():
            carta = entrada["carta"]
            ganador = entrada["jugador"]
            monto = entrada["mejor_oferta"]

            if ganador and ganador.gastar_oro(monto, f"compra subasta {carta.nombre}"):
                ganador.agregar_carta_al_banco(carta)
                log_evento(f"🏆 {ganador.nombre} gana {carta.nombre} por {monto} oro")
            else:
                manager_cartas.devolver_carta_al_pool(carta)
                log_evento(f"🔁 {carta.nombre} no fue vendida, vuelve al pool")

    def ver_estado_actual(self) -> List[str]:
        return [
            f"{data['carta'].nombre} (ID: {cid}) - Mejor oferta: {data['mejor_oferta']}"
            for cid, data in self.cartas_subastadas.items()
        ]

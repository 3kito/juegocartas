from enum import Enum
from typing import Optional

from .behavior_component import BehaviorComponent
from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion
from src.game.combate.ia.ia_utilidades import atacar_si_en_rango


class CombatBehavior(Enum):
    AGRESIVO = "agresivo"
    DEFENSIVO = "defensivo"
    GUARDIAN = "guardian"
    IGNORAR = "ignorar"


class CombatProcessor(BehaviorComponent):
    def __init__(self, tipo: CombatBehavior):
        self.tipo = tipo

    def ejecutar(self, carta, tablero, info_entorno) -> list[Interaccion]:
        enemigos = info_entorno.get("enemigos_en_rango", [])
        resultado: list[Interaccion] = []
        if self.tipo == CombatBehavior.IGNORAR:
            return resultado
        if self.tipo == CombatBehavior.DEFENSIVO:
            if carta.stats_combate.get("dano_recibido", 0) > 0 and enemigos:
                objetivo = enemigos[0]
                if atacar_si_en_rango(carta, objetivo):
                    resultado.append(
                        Interaccion(
                            fuente_id=carta.id,
                            objetivo_id=objetivo.id,
                            tipo=TipoInteraccion.ATAQUE,
                            metadata={"dano_base": carta.dano_fisico_actual},
                        )
                    )
            return resultado
        if self.tipo in {CombatBehavior.AGRESIVO, CombatBehavior.GUARDIAN}:
            if enemigos:
                objetivo = enemigos[0]
                if not atacar_si_en_rango(carta, objetivo):
                    if not (
                        carta.tiene_orden_manual()
                        or carta.tiene_orden_simulada()
                        or carta.tiene_evento_activo("movimiento")
                        or (
                            carta.orden_actual is not None
                            and carta.orden_actual.get("progreso") == "ejecutando"
                        )
                    ):
                        carta.marcar_orden_simulada("mover", objetivo.coordenada)
                resultado.append(
                    Interaccion(
                        fuente_id=carta.id,
                        objetivo_id=objetivo.id,
                        tipo=TipoInteraccion.ATAQUE,
                        metadata={"dano_base": carta.dano_fisico_actual},
                    )
                )
        return resultado

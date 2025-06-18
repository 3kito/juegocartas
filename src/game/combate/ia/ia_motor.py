from src.game.combate.comportamientos.behavior_executor import BehaviorExecutor

_executor = BehaviorExecutor()

def generar_interacciones_para(carta, tablero):
    """Genera interacciones automáticas para la carta."""
    if not carta.esta_viva():
        return []
    return _executor.ejecutar(carta, tablero)

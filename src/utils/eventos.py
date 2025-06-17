from typing import Callable, Any, Dict, List

_suscriptores: Dict[str, List[Callable[..., Any]]] = {}


def suscribir(evento: str, callback: Callable[..., Any]) -> None:
    """Registra un callback para un evento."""
    _suscriptores.setdefault(evento, []).append(callback)


def desuscribir(evento: str, callback: Callable[..., Any]) -> None:
    """Elimina un callback de la lista de suscriptores."""
    if evento in _suscriptores:
        _suscriptores[evento] = [cb for cb in _suscriptores[evento] if cb != callback]


def disparar(evento: str, **datos: Any) -> None:
    """Dispara un evento invocando todos sus suscriptores."""
    for cb in list(_suscriptores.get(evento, [])):
        try:
            cb(**datos)
        except Exception as e:
            from .helpers import log_evento
            log_evento(f"Error en callback de '{evento}': {e}", "ERROR")


"""Expose key combat classes with lazy imports to avoid circular deps."""

from __future__ import annotations

import importlib

__all__ = [
    "GestorInteracciones",
    "Interaccion",
    "TipoInteraccion",
    "MotorTiempoReal",
    "MapaGlobal",
]


def __getattr__(name: str):
    """Lazily load modules on attribute access."""
    if name == "GestorInteracciones":
        mod = importlib.import_module(".interacciones.gestor_interacciones", __name__)
        return mod.GestorInteracciones
    if name in {"Interaccion", "TipoInteraccion"}:
        mod = importlib.import_module(".interacciones.interaccion_modelo", __name__)
        return getattr(mod, name)
    if name == "MotorTiempoReal":
        mod = importlib.import_module(".motor.motor_tiempo_real", __name__)
        return mod.MotorTiempoReal
    if name == "MapaGlobal":
        mod = importlib.import_module(".mapa.mapa_global", __name__)
        return mod.MapaGlobal
    raise AttributeError(f"module {__name__} has no attribute {name}")

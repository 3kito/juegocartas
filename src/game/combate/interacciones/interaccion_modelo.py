# interacciones/interaccion_modelo.py

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time


class TipoInteraccion(Enum):
    ATAQUE = auto()
    HABILIDAD = auto()
    EFECTO_AREA = auto()
    ESTADO = auto()
    MOVIMIENTO = auto()


@dataclass
class Interaccion:
    fuente_id: int                      # ID de la carta que inicia la interacción
    objetivo_id: int                    # ID de la carta que recibe la interacción
    tipo: TipoInteraccion              # Tipo de interacción (ataque, habilidad, etc.)
    timestamp: float = field(default_factory=lambda: time.time())  # Momento de creación
    metadata: Dict[str, Any] = field(default_factory=dict)         # Datos adicionales opcionales

    def __str__(self):
        return (f"Interaccion({self.tipo.name}, fuente={self.fuente_id}, "
                f"objetivo={self.objetivo_id}, metadata={self.metadata})")

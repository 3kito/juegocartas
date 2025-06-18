from abc import ABC, abstractmethod


class BehaviorComponent(ABC):
    """Base abstracta para componentes de comportamiento."""

    @abstractmethod
    def ejecutar(self, carta, tablero, info_entorno):
        """Ejecuta el comportamiento para la carta."""
        raise NotImplementedError

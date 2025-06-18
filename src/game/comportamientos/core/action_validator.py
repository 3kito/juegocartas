class ActionValidator:
    """Basic action validator placeholder."""

    def can_act(self, carta, current_time: float) -> bool:
        return getattr(carta, "esta_viva", lambda: True)()

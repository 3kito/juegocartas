from ..core.base_interface import BaseInterface


class ConsoleInterface(BaseInterface):
    """Simple console-based interface."""

    def update_game_state(self, game_state):
        pass

    def handle_user_input(self):
        pass

    def display_message(self, message: str):
        print(message)

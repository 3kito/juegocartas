from abc import ABC, abstractmethod


class BaseInterface(ABC):
    @abstractmethod
    def update_game_state(self, game_state):
        pass

    @abstractmethod
    def handle_user_input(self):
        pass

    @abstractmethod
    def display_message(self, message: str):
        pass

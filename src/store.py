

class Store:
    # Nécessaire pour le démarrage
    slices_history: list[dict[str, dict[str, str]]] = []

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save_history()

    def format_history(self) -> dict[str, dict[str, str]]:
        return {key: value.__dict__ for (key, value) in self.__dict__.items()}.copy()

    def save_history(self) -> None:
        self.slices_history.append(self.format_history())


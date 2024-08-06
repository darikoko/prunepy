class Store:
    slices_history: list[dict[str, dict[str, str]]] = []

    def __init__(self, slices: dict[str, object]) -> None:
        self.slices = slices
        self.save_history()

    @staticmethod
    def format_slices(slices: dict[str, object]) -> dict[str, dict[str, str]]:
        return {key: value.__dict__ for (key, value) in slices.items()}.copy()

    def save_history(self) -> None:
        self.slices_history.append(self.format_slices(self.slices))


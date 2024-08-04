print("salut")

class Pizza:
    def __init__(self,name:str, taste:str) -> None:
        self.name = name
        self.taste = taste

class User:
    def __init__(self, pseudo:str) -> None:
        self.pseudo = pseudo

class Store:
    def __init__(self, slices: dict[str, any]) -> None:
        self.state = state


store = Store(
    {"pizza": {"size": "XL", "taste": "Cheese"}, "user": {"pseudo": "darikol"}}
)

print("salut")


class Store:
    def __init__(self, slices: dict[str, object]) -> None:
        self.slices = slices

    def alert(self, text:str):
        print(text)


class Subject:
    store: Store | None = None
    
    def register_store(self, store:Store):
        self.store = store

    def notify(self):
        store.alert("NOTIFICATION")


class Pizza(Subject):
    def __init__(self, name: str, taste: str) -> None:
        self.name = name
        self.taste = taste

    def change(self):
        self.taste = "Salmon"
        self.notify()


class User(Subject):
    def __init__(self, pseudo: str) -> None:
        self.pseudo = pseudo





pizza = Pizza("XL", "Peperonni")
user = User("darikol")
store = Store({"pizza": pizza, "user": user})
store.slices["pizza"].change()
print(store.slices["pizza"].taste)
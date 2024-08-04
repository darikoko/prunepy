import copy


def format_slices(slices: dict[str, object]) -> dict[str, dict[str,str]]:
    return {key:copy.deepcopy(value).__dict__ for (key,value) in slices.items()}

def log_method_call(func):
    def wrapper(self, *args, **kwargs):
        print(f"Calling {func.__name__} with instance {self}...")
        result = func(self, *args, **kwargs)
        print(f"{func.__name__} finished. Result: {result}")
        return result
    return wrapper

class Store:
    def __init__(self, slices: dict[str, object]) -> None:
        self.slices = slices
        self.slices_history : list[dict[str, dict[str,str]]] = [format_slices(slices)]

    def alert(self, text:str):
        print(text)

    def save_history(self) -> None:
        self.slices_history.append(format_slices(self.slices))


class Subject:
    store: Store | None = None
    
    def register_store(self, store:Store):
        self.store = store

    def notify(self):
        store.alert("NOTIFICATION")
        store.save_history()


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
print(store.slices_history)
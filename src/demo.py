from prune import Prune, notify
from pyscript import fetch, document
import asyncio



class Pizza:
    def __init__(self, name: str, taste: str) -> None:
        self.name = name
        self.taste = taste
        self.reviews = ["ok", "cool", "super", "bof"]

    @notify
    def change(self):
        self.taste = "Salmon"

    @notify
    def change_by_value(self, value: str):
        self.taste = value


class User:
    def __init__(self, pseudo: str) -> None:
        self.pseudo = pseudo
        self.show = False

    @notify
    def toggle(self):
        self.show = not self.show

class Todo:
    def __init__(self) -> None:
        self.tasks:list[str] = []

    @notify
    def add_task(self, input) -> None:
        self.tasks.append(input.value)
        input.value = ""

pizza = Pizza("XL", "Peperonni")
user = User("darikol")
todo = Todo()
prunoe = Prune({"pizza": pizza, "user": user, "todo":todo})









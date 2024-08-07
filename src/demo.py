from prune import Prune, notify
from pyscript import fetch
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


pizza = Pizza("XL", "Peperonni")
user = User("darikol")
prune = Prune({"pizza": pizza, "user": user})

async def oula():
    response = await fetch("http://nimbus/api/")
    if response.ok:
        data = await response.text()
        print(data)
        return data
    else:
        return "Oups"

print(fetch("http://nimbus/api/"),"Chouette")

response = await fetch("https://jsonplaceholder.typicode.com/todos/1")
if response.ok:
    data = await response.text()
    print(data)
else:
    print(response.status)





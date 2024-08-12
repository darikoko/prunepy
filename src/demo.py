from prune import Prune, notify
from pyscript import fetch, document, window



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

    def show_text(self,text):
        print(text)


class Task:
    def __init__(self,text:str, done:bool  = False) -> None:
        self.text = text
        self.done = done

class Todo:
    def __init__(self) -> None:
        self.tasks:list[Task] = []

    @notify
    def add_task(self, input) -> None:
        self.tasks.append(Task(input.value))
        input.value = ""

    @notify
    def remove_task(self, index:int):
        self.tasks.pop(index)

    @notify
    def complete_task(self, index:int):
        task = self.tasks[index]
        task.done = not task.done


class Clock:
    def __init__(self) -> None:
        self.seconds_deg = 0
        self.minutes_deg = 0
        self.hours_deg = 0
        window.setInterval(self.say_coucou, 1000, "OK")

    def say_coucou(self,time):
        self.seconds_deg += 360/60
        self.minutes_deg += 360/60/60
        print(self.__dict__)
        print("coucou")

pizza = Pizza("XL", "Peperonni")
user = User("darikol")
todo = Todo()
prunoe = Prune( pizza=pizza, user=user, todo=todo)


clock = Clock()










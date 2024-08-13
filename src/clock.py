from pyscript import window
from prune import Prune, notify
class Clock:
    def __init__(self) -> None:
        self.seconds_deg = 0
        self.minutes_deg = 0
        self.hours_deg = 0
        # Si on veut on peut passer des arguments derrière le temps, ce sera envoyé à event
        window.setInterval(self.refresh_clock, 1000)

    @notify
    def refresh_clock(self):
        self.seconds_deg += 360/60
        self.minutes_deg += 360/(60*60)
        self.hours_deg += 360/(60*60*12)

    @notify
    def set_hour(self, hour:str):
        self.hours_deg = 360/12 * int(hour)

    @notify
    def set_minute(self, minute:str):
        self.minutes_deg = 360/60 * int(minute)

    @notify
    def set_second(self, second:str):
        self.seconds_deg = 360/60 * int(second)

clock = Clock()
prune = Prune( clock=clock)

# Example 'hey' variable
hey = ('a', 'b', 'c')

# Example list of tuples
my_list = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

# Unpacking in a for loop
for items in my_list:
    # Unpack dynamically using the length of 'hey'
    locals().update(dict(zip(hey, items)))
    print(locals())
    # Now you can use a, b, c, etc.
    print(a, b, c)

exec("k = 14")
print(k)


from pyscript import window, document
from pyscript.ffi import create_proxy


# Arbre et feuilles
# L'arbre de représentation
ZEPHYR_DIRECTIVES = [
    "n-text",
    "n-html",
    "n-show",
]

JS_EVENTS = [
    "abort",
    "afterprint",
    "animationend",
    "animationiteration",
    "animationstart",
    "beforeprint",
    "beforeunload",
    "blur",
    "canplay",
    "canplaythrough",
    "change",
    "click",
    "contextmenu",
    "copy",
    "cut",
    "dblclick",
    "drag",
    "dragend",
    "dragenter",
    "dragleave",
    "dragover",
    "dragstart",
    "drop",
    "durationchange",
    "ended",
    "error",
    "focus",
    "focusin",
    "focusout",
    "fullscreenchange",
    "fullscreenerror",
    "hashchange",
    "input",
    "invalid",
    "keydown",
    "keypress",
    "keyup",
    "load",
    "loadeddata",
    "loadedmetadata",
    "loadstart",
    "message",
    "mousedown",
    "mouseenter",
    "mouseleave",
    "mousemove",
    "mouseover",
    "mouseout",
    "mouseup",
    "mousewheel",
    "offline",
    "online",
    "open",
    "pagehide",
    "pageshow",
    "paste",
    "pause",
    "play",
    "playing",
    "popstate",
    "progress",
    "ratechange",
    "resize",
    "reset",
    "scroll",
    "search",
    "seeked",
    "seeking",
    "select",
    "stalled",
    "storage",
    "submit",
    "suspend",
    "timeupdate",
    "toggle",
    "touchcancel",
    "touchend",
    "touchmove",
    "touchstart",
    "transitionend",
    "unload",
    "volumechange",
    "waiting",
    "wheel",
]


class Tree:
    def __init__(self) -> None:
        self.leaves: list[Leaf] = []
        self.build_tree()

    def build_tree(self):
        selector = ", ".join(
            f"[{directive}]" for directive in ZEPHYR_DIRECTIVES
        ) + "," + ", ".join(f"[n-on{event}]" for event in JS_EVENTS)
        print(selector)
        html_elements = document.querySelectorAll(selector)
        for html_element in html_elements:
            leaf = Leaf(html_element)
            self.leaves.append(leaf)
        self.global_render()

    def global_render(self):
        for leaf in self.leaves:
            print(leaf)
            leaf.render()


class Leaf:
    def __init__(self, html_element) -> None:
        self.html_element = html_element
        self.directives: dict[str, str] = {}
        self.find_directives()

    def find_directives(self):
        # ici on itere pas sur JSEVENTS donc ils sont ignorés
        for directive in ZEPHYR_DIRECTIVES + [f"n-on{event}" for event in JS_EVENTS]:
            if (
                attribute_value := self.html_element.getAttribute(directive)
            ) is not None:
                self.directives[directive] = attribute_value
        print(self.directives)

    @staticmethod
    def handle_event(event):
        function = event.target.getAttribute("n-on" + event.type)
        print(function)
        eval(function, {"store": store}, {"event": event})

    def render(self):
        for directive_name, directive_value in self.directives.items():
            print(directive_name)
            if directive_name == "n-text":
                self.html_element.innerText = eval(directive_value)
            elif directive_name == "n-html":
                self.html_element.innerHTML = eval(directive_value)
            elif directive_name == "n-show":
                self.html_element.hidden = not eval(directive_value)
            elif directive_name.startswith("n-on"):
                event_type = directive_name.replace("n-on", "")
                self.html_element.addEventListener(event_type, Leaf.handle_event)
            else:
                print("oups")


# Store et companie


def format_slices(slices: dict[str, object]) -> dict[str, dict[str, str]]:
    return {key: value.__dict__ for (key, value) in slices.items()}.copy()


def notify(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._store.save_history()
        self._store.tree.global_render()

    return wrapper


class Store:
    def __init__(self, slices: dict[str, object]) -> None:
        self.slices = slices
        for obj in self.slices.values():
            obj.register_store(self)
        self.slices_history: list[dict[str, dict[str, str]]] = [format_slices(slices)]

    def start(self):
        self.tree = Tree()

    def save_history(self) -> None:
        self.slices_history.append(format_slices(self.slices))
        print(self.slices_history)


# Les observables


class Subject:
    _store: Store | None = None

    def register_store(self, store: Store):
        self._store = store


class Pizza(Subject):
    def __init__(self, name: str, taste: str) -> None:
        self.name = name
        self.taste = taste

    @notify
    def change(self):
        self.taste = "Salmon"

    @notify
    def change_by_value(self, value: str):
        self.taste = value


class User(Subject):
    def __init__(self, pseudo: str) -> None:
        self.pseudo = pseudo
        self.show = False

    @notify
    def toggle(self):
        self.show = not self.show


pizza = Pizza("XL", "Peperonni")
user = User("darikol")
jack = "salulululsf"
store = Store({"pizza": pizza, "user": user})
store.start()

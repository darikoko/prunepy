import copy
from pyscript import window, document

# Store et companie


def format_slices(slices: dict[str, object]) -> dict[str, dict[str, str]]:
    return {key: copy.deepcopy(value).__dict__ for (key, value) in slices.items()}


def notify(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._store.save_history()

    return wrapper


class Store:
    def __init__(self, slices: dict[str, object]) -> None:
        self.slices = slices
        for obj in self.slices.values():
            obj.register_store(self)
        self.slices_history: list[dict[str, dict[str, str]]] = [format_slices(slices)]

    def save_history(self) -> None:
        self.slices_history.append(format_slices(self.slices))


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


class User(Subject):
    def __init__(self, pseudo: str) -> None:
        self.pseudo = pseudo
        self.show = False
    
    @notify
    def toggle(self):
        self.show = not self.show




# L'arbre de représentation
ZEPHYR_DIRECTIVES = [
        "n-text",
        "n-html",
        "n-show",
    ]


class Tree:
    def __init__(self) -> None:
        self.leaves : list[Leaf] = []
        self.build_tree()

    def build_tree(self):
        selector = ", ".join(f"[{directive}]" for directive in ZEPHYR_DIRECTIVES)
        html_elements = document.querySelectorAll(selector)
        for html_element in html_elements:
            leaf = Leaf(html_element)
            self.leaves.append(leaf)
        self.global_render()

    def global_render(self):
        for leaf in self.leaves:
            leaf.render()


class Leaf:
    

    def __init__(self, html_element) -> None:
        self.html_element = html_element
        self.directives : dict[str, str] = {}
        self.find_directives()

    def find_directives(self):
        for directive in ZEPHYR_DIRECTIVES:
            if (attribute_value := self.html_element.getAttribute(directive)) is not None:
                self.directives[directive] = attribute_value
        print(self.directives)

    def render(self):
        for directive_name, directive_value in self.directives.items():
            match directive_name:
                case "n-text":
                    self.html_element.innerText = eval(directive_value)
                case "n-html":
                    self.html_element.innerHTML = eval(directive_value)
                case "n-show":
                    self.html_element.hidden = not eval(directive_value)
                case _ :
                    print("oups")


pizza = Pizza("XL", "Peperonni")
user = User("darikol")
store = Store({"pizza": pizza, "user": user})
store.slices["pizza"].change()
# print(store.slices["pizza"].taste)
# print(store.slices_history)



arbre = Tree()
print(arbre.leaves)

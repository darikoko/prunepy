import datetime
from pyscript import document
import time
from oh import SAY

print(SAY)

# Arbre et feuilles
# L'arbre de représentation


class Tree:
    def __init__(self) -> None:
        self.leaves: list[Leaf] = []
        self.tree_scope: dict[str, any] = {}
        self.build_tree()

    def is_prune(self, element) -> bool:
        for attribute in element.attributes:
            if attribute.name.startswith("n-"):
                return True
        return False

    # Peut etre selectionner d'abord les div marquees par un attribut pour alleger le parsing
    # on pourrait faire un attribut zephyr ou autre
    def build_tree(self):
        for html_element in document.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element)
                self.leaves.append(leaf)
        self.mutate_dom()

    def mutate_dom(self):
        for leaf in self.leaves:
            print(leaf)
            leaf_scope = leaf.render(self.tree_scope)
            print(leaf_scope, "REAL LEAF")
            if len(leaf_scope) != 0:
                self.tree_scope.update(leaf_scope)


class Leaf:
    def __init__(self, html_element) -> None:
        self.html_element = html_element
        self.directives: dict[str, str] = {}
        self.initial_html_classes = self.html_element.classList.value
        print(self.initial_html_classes, "init")
        self.find_directives()

    def get_prune_attributes(self) -> list[str]:
        return [
            attribute.name
            for attribute in self.html_element.attributes
            if attribute.name.startswith("n-")
        ]

    def find_directives(self):
        for directive in self.get_prune_attributes():
            if (
                attribute_value := self.html_element.getAttribute(directive)
            ) is not None:
                self.directives[directive] = attribute_value
        print(self.directives)

    @staticmethod
    def handle_event(event):
        function = event.target.getAttribute("n-on:" + event.type)
        print(function)
        eval(function, None, {"event": event})

    def render(self, tree_scope: dict[str, any] = {}):
        leaf_scope = {}
        for directive_name, directive_value in self.directives.items():
            print(directive_name)
            if directive_name == "n-text":
                self.html_element.innerText = eval(directive_value, None, tree_scope)
            elif directive_name == "n-html":
                self.html_element.innerHTML = eval(directive_value, None, tree_scope)
            elif directive_name == "n-show":
                self.html_element.hidden = not eval(directive_value, None, tree_scope)
            elif directive_name.startswith("n-on:"):
                event_type = directive_name.replace("n-on:", "")
                self.html_element.addEventListener(event_type, Leaf.handle_event)
            elif directive_name.startswith("n-bind:"):
                attribute_to_bind = directive_name.replace("n-bind:", "")
                if attribute_to_bind == "class":
                    self.html_element.setAttribute(
                        "class",
                        self.initial_html_classes
                        + eval(directive_value, None, tree_scope),
                    )
                else:
                    self.html_element.setAttribute(
                        attribute_to_bind, eval(directive_value, None, tree_scope)
                    )
            elif directive_name == "n-for":
                splitted_for = directive_value.split(" in ")
                list_element = eval(splitted_for[1], None, tree_scope)
                initial_inner_html = self.html_element.innerHTML
                print(initial_inner_html, "innerHTML")
                for i in list_element:
                    leaf_scope[splitted_for[0]] = i
                    print(i, "AHHHHHHHHHHH")
            else:
                print("oups")

        print(leaf_scope, "LEAF SCOPE")
        return leaf_scope


# Store et companie


def notify(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._store.save_history()
        self._store.tree.mutate_dom()

    return wrapper


# Ne devrait pas avoir connaissance de Tree, la gestion des evenements devrait
# se faire pas un objet qui wrapperait Store et Tree
class Store:
    slices_history: list[dict[str, dict[str, str]]] = []

    def __init__(self, slices: dict[str, object]) -> None:
        self.slices = slices
        self.register_store_to_slices()
        self.save_history()

    def register_store_to_slices(self):
        for slice in self.slices.values():
            slice._store = self

    @staticmethod
    def format_slices(slices: dict[str, object]) -> dict[str, dict[str, str]]:
        return {key: value.__dict__ for (key, value) in slices.items()}.copy()

    def start(self):
        self.tree = Tree()

    def save_history(self) -> None:
        self.slices_history.append(self.format_slices(self.slices))
        print(self.slices_history)


# Les observables


class Pizza:
    def __init__(self, name: str, taste: str) -> None:
        self.name = name
        self.taste = taste
        self.reviews = ["ok", "cool", "super"]

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
jack = "salulululsf"
store = Store({"pizza": pizza, "user": user})
store.start()

print(time.localtime())
print(datetime.date.today())

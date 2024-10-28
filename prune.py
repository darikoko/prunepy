from pyscript import document

class Store:
    # Nécessaire pour le démarrage
    slices_history: list[dict[str, dict[str, str]]] = []

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save_history()

    def format_history(self) -> dict[str, dict[str, str]]:
        return {key: value.__dict__ for (key, value) in self.__dict__.items()}.copy()

    def save_history(self) -> None:
        self.slices_history.append(self.format_history())



class Tree:
    def __init__(self) -> None:
        self.leaves: list[Leaf] = []
        self.latest_leaves: list[Leaf] = []
        self.build_tree()
        self.local_scope = {}

    def is_prune(self, element) -> bool:
        for attribute in element.attributes:
            if attribute.name.startswith("p-") or attribute.name.startswith("@") or attribute.name.startswith(":"):
                return True
        return False

    # Peut etre selectionner d'abord les div marquees par un attribut pour alleger le parsing
    # on pourrait faire un attribut zephyr ou autre
    def build_tree(self):
        for html_element in document.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element, {})
                self.leaves.append(leaf)

    def build_latest_leaves(self, element, local_scope):
        self.local_scope.update(local_scope)
        new_scope = self.local_scope.copy()
        leaf = Leaf(element, new_scope)
        leaf.html_element.pruneLocalScope = local_scope
        self.latest_leaves.append(leaf)
        for html_element in element.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element, new_scope)
                leaf.html_element.pruneLocalScope = local_scope
                self.latest_leaves.append(leaf)


class Leaf:
    def __init__(self, html_element, local_scope={}) -> None:
        self.html_element = html_element
        self.directives: dict[str, str] = {}
        self.initial_html_classes = self.html_element.classList.value
        self.initial_n_for_content = None
        self.local_scope = local_scope
        self.find_directives()

    def get_prune_attributes(self) -> list[str]:
        return [
            attribute.name
            for attribute in self.html_element.attributes
            if (
                attribute.name.startswith("p-")
                or attribute.name.startswith("@")
                or attribute.name.startswith(":")
            )
        ]

    def find_directives(self):
        for directive in self.get_prune_attributes():
            if (
                attribute_value := self.html_element.getAttribute(directive)
            ) is not None:
                self.directives[directive] = attribute_value

def notify(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._app.store.save_history()
        self._app.render()

    return wrapper


class Refs:
    pass

class Prune:
    global_scope = {}

    def __init__(self, **kwargs) -> None:
        self.store = Store(**kwargs)
        self.register_app_to_slices()
        self.tree = Tree()
        Prune.global_scope = {"store": self.store, "refs": Refs()}
        self.render()

    def register_app_to_slices(self):
        for attr in self.store.__dict__:
            slice = getattr(self.store, attr)
            slice._app = self

    @staticmethod
    def handle_event(event):
        function = event.currentTarget.getAttribute("p-on:" + event.type)
        # Au cas ou la syntaxe @ est utlilisée
        if function is None:
            function = event.currentTarget.getAttribute("@" + event.type)
        # Passer le local_scope ici
        local_scope = {"event": event} | event.currentTarget.pruneLocalScope if hasattr(event.target, "pruneLocalScope") else {"event":event}
        eval(function, Prune.global_scope, local_scope)

    def remove_latest_leaves(self):
        for leaf in self.tree.latest_leaves:
            leaf.html_element.remove()
        self.tree.latest_leaves = []

    def render(self):
        self.remove_latest_leaves()
        for leaf in self.tree.leaves:
            self.process_leaf(leaf)
        for leaf in self.tree.latest_leaves:
            self.process_leaf(leaf)

    def process_leaf(self, leaf):
        for directive_name, directive_value in leaf.directives.items():
            if directive_name == "p-text":
                leaf.html_element.innerText = eval(
                    directive_value, Prune.global_scope, leaf.local_scope
                )
            elif directive_name == "p-html":
                leaf.html_element.innerHTML = eval(
                    directive_value, Prune.global_scope, leaf.local_scope
                )
            elif directive_name == "p-show":
                leaf.html_element.hidden = not eval(
                    directive_value, Prune.global_scope, leaf.local_scope
                )
            elif directive_name == "p-ref":
                #Prune.global_scope["refs"][directive_value] = leaf.html_element
                setattr(Prune.global_scope["refs"], directive_value, leaf.html_element)
            elif directive_name.startswith("p-on:") or directive_name.startswith("@"):
                event_type = directive_name.replace("p-on:", "").replace("@", "")
                leaf.html_element.addEventListener(event_type, self.handle_event)
            elif directive_name.startswith("p-bind:") or directive_name.startswith(":"):
                attribute_to_bind = directive_name.replace("p-bind:", "").replace(":","")
                if attribute_to_bind == "class":
                    leaf.html_element.setAttribute(
                        "class",
                        leaf.initial_html_classes
                        + eval(directive_value, Prune.global_scope, leaf.local_scope),
                    )
                else:
                    leaf.html_element.setAttribute(
                        attribute_to_bind,
                        eval(directive_value, Prune.global_scope, leaf.local_scope),
                    )
            elif directive_name == "p-for":
                iteration_name, list_name = directive_value.split(" in ")
                keys = iteration_name.replace("(","").replace(")","").split(",")
                my_list =  eval(list_name, Prune.global_scope)
                for item in reversed(list(my_list)):
                    # si c'est une for loop avec un seul élément on doit utiliser le 2è choix
                    local_scope = dict(zip(keys, item)) if len(keys) > 1 else dict(zip(keys, (item,)))
                    clone = leaf.html_element.content.cloneNode(True)
                    inserted_html_element = leaf.html_element.parentNode.insertBefore(clone.children[0], leaf.html_element.nextSibling)
                    self.tree.build_latest_leaves(inserted_html_element, local_scope)
            elif directive_name == "p-if":
                clone = leaf.html_element.content.cloneNode(True)
                if eval(directive_value,Prune.global_scope, leaf.local_scope):
                    inserted_html_element = leaf.html_element.parentNode.insertBefore(clone.children[0], leaf.html_element.nextSibling)
                    self.tree.build_latest_leaves(inserted_html_element, {})

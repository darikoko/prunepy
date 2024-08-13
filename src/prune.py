from store import Store
from tree import Tree, Leaf


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
        function = event.target.getAttribute("p-on:" + event.type)
        # Au cas ou la syntaxe @ est utlilisée
        if function is None:
            function = event.target.getAttribute("@" + event.type)
        # Passer le local_scope ici
        local_scope = {"event": event} | event.target.pruneLocalScope if hasattr(event.target, "pruneLocalScope") else {"event":event}
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

from store import Store
from tree import Tree, Leaf



def notify(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._app.store.save_history()
        self._app.render()

    return wrapper




class Prune:
    global_scope = {}

    def __init__(self, slices: dict[str, object]) -> None:
        self.store = Store(slices)
        self.register_app_to_slices()
        self.tree = Tree()
        Prune.global_scope = {"store": self.store.slices, "refs": {}}
        self.tree_scope = {}
        self.render()

    def register_app_to_slices(self):
        for slice in self.store.slices.values():
            slice._app = self

    @staticmethod
    def handle_event(event):
        function = event.target.getAttribute("n-on:" + event.type)
        eval(function, Prune.global_scope, {"event": event})

    def remove_latest_leaves(self):
        for leaf in self.tree.latest_leaves:
            leaf.html_element.remove()

    def render(self):
        self.remove_latest_leaves()
        for leaf in self.tree.leaves:
            self.process_leaf(leaf)
        for leaf in self.tree.latest_leaves:
            self.process_leaf(leaf)

    def process_leaf(self, leaf):
        for directive_name, directive_value in leaf.directives.items():
            if directive_name == "n-text":
                print(directive_value)

                leaf.html_element.innerText = eval(
                        directive_value, Prune.global_scope, self.tree_scope
                    )
            elif directive_name == "n-html":
                leaf.html_element.innerHTML = eval(
                        directive_value, Prune.global_scope, self.tree_scope
                    )
            elif directive_name == "n-show":
                leaf.html_element.hidden = not eval(
                        directive_value, Prune.global_scope, self.tree_scope
                    )
            elif directive_name == "n-ref":
                Prune.global_scope["refs"][directive_value] = leaf.html_element
            elif directive_name.startswith("n-on:"):
                event_type = directive_name.replace("n-on:", "")
                leaf.html_element.addEventListener(event_type, self.handle_event)
            elif directive_name.startswith("n-bind:"):
                attribute_to_bind = directive_name.replace("n-bind:", "")
                if attribute_to_bind == "class":
                    leaf.html_element.setAttribute(
                            "class",
                            leaf.initial_html_classes
                            + eval(
                                directive_value, Prune.global_scope, self.tree_scope
                            ),
                        )
                else:
                    leaf.html_element.setAttribute(
                            attribute_to_bind,
                            eval(directive_value, Prune.global_scope, self.tree_scope),
                        )
            elif directive_name == "n-for":
                iteration_name, list_name = directive_value.split(" in ")
                list_element = eval(list_name, Prune.global_scope, self.tree_scope)
                template = leaf.html_element
                for index, i in reversed(list(enumerate(list_element))):
                    clone = template.content.cloneNode(True)
                    inserted_html_element = template.parentNode.insertBefore(
                            clone.children[0], template.nextSibling
                        )
                    leaf = Leaf(inserted_html_element)
                    leaf.replace_iteration_variable(iteration_name, f"{list_name}[{index}]")
                    self.tree.latest_leaves.append(leaf)
            else:
                pass
    
    

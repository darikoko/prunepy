from store import Store
from tree import Tree


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
        self.tree = Tree(self.store)
        Prune.global_scope = {"prune":self.store}
        self.tree_scope = {}
        self.render()

    def register_app_to_slices(self):
        for slice in self.store.slices.values():
            slice._app = self

    @staticmethod
    def handle_event(event):
        function = event.target.getAttribute("n-on:" + event.type)
        eval(function, Prune.global_scope, {"event": event})


    def render(self):
        leaf_scope = {}
        for leave in self.tree.leaves:
            for directive_name, directive_value in leave.directives.items():
                if directive_name == "n-text":
                    leave.html_element.innerText = eval(
                        directive_value, Prune.global_scope, self.tree_scope
                    )
                elif directive_name == "n-html":
                    leave.html_element.innerHTML = eval(
                        directive_value, Prune.global_scope, self.tree_scope
                    )
                elif directive_name == "n-show":
                    leave.html_element.hidden = not eval(
                        directive_value, Prune.global_scope, self.tree_scope
                    )
                elif directive_name.startswith("n-on:"):
                    print("ONNN")
                    event_type = directive_name.replace("n-on:", "")
                    leave.html_element.addEventListener(event_type, self.handle_event)
                elif directive_name.startswith("n-bind:"):
                    attribute_to_bind = directive_name.replace("n-bind:", "")
                    if attribute_to_bind == "class":
                        leave.html_element.setAttribute(
                            "class",
                            leave.initial_html_classes
                            + eval(directive_value, Prune.global_scope, self.tree_scope),
                        )
                    else:
                        leave.html_element.setAttribute(
                            attribute_to_bind,
                            eval(directive_value, Prune.global_scope, self.tree_scope),
                        )
                elif directive_name == "n-for":
                    splitted_for = directive_value.split(" in ")
                    list_element = eval(
                        splitted_for[1], Prune.global_scope, self.tree_scope
                    )
                    initial_inner_html = leave.html_element.innerHTML
                    for i in list_element:
                        leaf_scope[splitted_for[0]] = i
                else:
                    pass

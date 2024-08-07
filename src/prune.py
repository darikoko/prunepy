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
                    iteration_name, list_name = directive_value.split(" in ")
                    list_element = eval(
                        list_name, Prune.global_scope, self.tree_scope
                    )
                    for index,i in enumerate(list_element):
                        clone = leave.html_element.content.cloneNode(True)
                        leave.html_element.after(clone)
                        print(clone)
                        #leave.html_element.appendChild(leave.initial_n_for_content)
                        """
                        self.tree_scope[iteration_name] = list_element[index]
                        print(self.tree_scope)
                        clone = leave.html_element.firstElementChild.cloneNode(True)
                        clone.id = i
                        clone.setAttribute("n-for-iteration", iteration_name)
                        print(clone)
                        leave.html_element.after(clone)
                        print(i,"JE ME LANCE")
                        """
                else:
                    pass

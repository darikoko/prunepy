from store import Store
from tree import Tree, Leaf
from parser import extract_loop


def notify(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._app.store.save_history()
        self._app.render()

    return wrapper


class Prune:
    global_scope = {}

    def __init__(self, **kwargs) -> None:
        self.store = Store(**kwargs)
        self.register_app_to_slices()
        self.tree = Tree()
        Prune.global_scope = {"store": self.store, "refs": {}}
        self.tree_scope = {}
        self.render()

    def register_app_to_slices(self):
        for attr in self.store.__dict__:
            slice = getattr(self.store, attr)
            print(getattr(self.store, attr))
            print(attr)
            slice._app = self

    @staticmethod
    def handle_event(event):
        function = event.target.getAttribute("n-on:" + event.type)
        # Au cas ou la syntaxe @ est utlilisée
        if function is None:
            function = event.target.getAttribute("@" + event.type)
        eval(function, Prune.global_scope, {"event": event})

    def remove_latest_leaves(self):
        for leaf in self.tree.latest_leaves:
            leaf.html_element.remove()

    def render(self):
        self.remove_latest_leaves()
        for leaf in self.tree.leaves:
            self.process_leaf(leaf)
        for leaf in self.tree.latest_leaves:
            print(leaf.local_scope,"okay")
            self.process_leaf(leaf)
            

    @staticmethod
    def for_loop_string(iteration_name:str, list_name:str):
        local_scope = extract_loop(iteration_name)
        text = f"""for {iteration_name} in {list_name}:\n\tclone = template.content.cloneNode(True)\n\tinserted_html_element = template.parentNode.insertBefore(clone.children[0], template.nextSibling)\n\tleaf = Leaf(inserted_html_element)\n\tleaf.local_scope={local_scope}\n\tself.tree.latest_leaves.append(leaf)\n\t"""
        print(text)
        return text

    def process_leaf(self, leaf):
        for directive_name, directive_value in leaf.directives.items():
            if directive_name == "n-text":
                print(directive_value)

                leaf.html_element.innerText = eval(
                    directive_value, Prune.global_scope, leaf.local_scope
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
            elif directive_name.startswith("n-on:") or directive_name.startswith("@"):
                print(directive_name, "GP")
                event_type = directive_name.replace("n-on:", "").replace("@", "")
                print(event_type, "EVENT TYPE")
                leaf.html_element.addEventListener(event_type, self.handle_event)
            elif directive_name.startswith("n-bind:") or directive_name.startswith(":"):
                attribute_to_bind = directive_name.replace("n-bind:", "").replace(":","")
                if attribute_to_bind == "class":
                    leaf.html_element.setAttribute(
                        "class",
                        leaf.initial_html_classes
                        + eval(directive_value, Prune.global_scope, self.tree_scope),
                    )
                else:
                    leaf.html_element.setAttribute(
                        attribute_to_bind,
                        eval(directive_value, Prune.global_scope, self.tree_scope),
                    )
            elif directive_name == "n-for":
                iteration_name, list_name = directive_value.split(" in ")
                template = leaf.html_element
                exec(Prune.for_loop_string(iteration_name, list_name), Prune.global_scope,{"leaf":leaf,"template":template, "Leaf": Leaf, "self":self})
            else:
                pass

        

    

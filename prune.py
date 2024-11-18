from pyscript import document
import inspect

async def aexec(code, merged_scope):
    # We create this dict to 
    # be able to call __ex(), because passing it
    # to the function will make it accessible from local_scope
    local_scope = {}
    exec(
        f'async def __ex(): ' +
        ''.join(f'\n {l}' for l in code.split('\n')),
    merged_scope, local_scope)
    # Get `__ex` from local_scope and call it 
    await local_scope['__ex']()

class Store:
    # Required for startup
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

    # Maybe mark the concerned div with specific attribute
    # to speedup the startup
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
        self._app.register_app_to_slices_new(self._app.store)
        self._app.render()
    return wrapper

def notify_async(func):
    async def wrapper(self, *args, **kwargs):
        await func(self, *args, **kwargs)
        self._app.store.save_history()
        self._app.register_app_to_slices_new(self._app.store)
        self._app.render()
    return wrapper


class Refs:
    pass



class Prune:
    global_scope = {}

    def __init__(self, global_scope={},**kwargs) -> None:
        self.store = Store(**kwargs)
        self.register_app_to_slices(self.store)
        self.tree = Tree()
        Prune.global_scope = {"store": self.store, "refs": Refs()} | global_scope
        self.render()

    def register_app_to_slices(self, obj):
        #TODO get only attributes which are doesnt start with _
        for attr in [x for x in obj.__dict__ if not x.startswith("_")]:
            slice = getattr(obj, attr)
            if hasattr(slice, "__dict__") :  # Check if is an object
                self.register_app_to_slices(slice)  # Recursive call
                slice._app = self
            elif isinstance(slice,list):
                for element in slice:
                    self.register_app_to_slices(element)  # Recursive call
                    element._app = self

 

    @staticmethod
    async def handle_event(event):
        function = event.currentTarget.getAttribute("p-on:" + event.type)
        # In the case where @ is used
        if function is None:
            function = event.currentTarget.getAttribute("@" + event.type)
        local_scope = {"event": event} | event.currentTarget.pruneLocalScope if hasattr(event.target, "pruneLocalScope") else {"event":event}
        merged_scope = Prune.global_scope | local_scope 
        await aexec(function , merged_scope)

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
                keys = iteration_name.replace("(","").replace(")","").replace(" ","").split(",")
                my_list =  eval(list_name, Prune.global_scope)
                for item in list(my_list):
                    # If it's a for loop with only one element we have to use the 2nd choice
                    local_scope = dict(zip(keys, item)) if len(keys) > 1 else dict(zip(keys, (item,)))
                    # We add the local scope of the leaf to retrieve iteration variables from a parent loop for example
                    local_scope = leaf.local_scope | local_scope 
                    clone = leaf.html_element.content.cloneNode(True)
                    inserted_html_element = leaf.html_element.parentNode.appendChild(clone.children[0])
                    self.tree.build_latest_leaves(inserted_html_element, local_scope)
            elif directive_name == "p-if":
                clone = leaf.html_element.content.cloneNode(True)
                if eval(directive_value,Prune.global_scope, leaf.local_scope):
                    inserted_html_element = leaf.html_element.parentNode.insertBefore(clone.children[0], leaf.html_element.nextSibling)
                    self.tree.build_latest_leaves(inserted_html_element, {})





from pyscript import document


class Tree:
    def __init__(self, store) -> None:
        self.leaves: list[Leaf] = []
        self.tree_scope: dict[str, any] = {}
        self.build_tree(store)

    def is_prune(self, element) -> bool:
        for attribute in element.attributes:
            if attribute.name.startswith("n-"):
                return True
        return False

    # Peut etre selectionner d'abord les div marquees par un attribut pour alleger le parsing
    # on pourrait faire un attribut zephyr ou autre
    def build_tree(self, store):
        print("BUILD")
        for html_element in document.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element, store)
                self.leaves.append(leaf)
        #self.mutate_dom()

    def mutate_dom(self ):
        print("MUTATE")
        for leaf in self.leaves:
            leaf_scope = leaf.render(self.tree_scope)
            if len(leaf_scope) != 0:
                self.tree_scope.update(leaf_scope)


class Leaf:
    def __init__(self, html_element, store) -> None:
        self.html_element = html_element
        self.global_scope = {"prune": store}
        self.directives: dict[str, str] = {}
        self.initial_html_classes = self.html_element.classList.value
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

    @staticmethod
    def handle_event(event):
        function = event.target.getAttribute("n-on:" + event.type)
        eval(function, None, {"event": event})

    def render(self, tree_scope: dict[str, any] = {}):
        leaf_scope = {}
        for directive_name, directive_value in self.directives.items():
            if directive_name == "n-text":
                self.html_element.innerText = eval(
                    directive_value, self.global_scope, tree_scope
                )
            elif directive_name == "n-html":
                self.html_element.innerHTML = eval(
                    directive_value, self.global_scope, tree_scope
                )
            elif directive_name == "n-show":
                self.html_element.hidden = not eval(
                    directive_value, self.global_scope, tree_scope
                )
            elif directive_name.startswith("n-on:"):
                print("ONNN")
                event_type = directive_name.replace("n-on:", "")
                self.html_element.addEventListener(event_type, Leaf.handle_event)
            elif directive_name.startswith("n-bind:"):
                attribute_to_bind = directive_name.replace("n-bind:", "")
                if attribute_to_bind == "class":
                    self.html_element.setAttribute(
                        "class",
                        self.initial_html_classes
                        + eval(directive_value, self.global_scope, tree_scope),
                    )
                else:
                    self.html_element.setAttribute(
                        attribute_to_bind,
                        eval(directive_value, self.global_scope, tree_scope),
                    )
            elif directive_name == "n-for":
                splitted_for = directive_value.split(" in ")
                list_element = eval(splitted_for[1], self.global_scope, tree_scope)
                initial_inner_html = self.html_element.innerHTML
                for i in list_element:
                    leaf_scope[splitted_for[0]] = i
            else:
                pass

        return leaf_scope

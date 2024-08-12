from pyscript import document


class Tree:
    def __init__(self) -> None:
        self.leaves: list[Leaf] = []
        self.latest_leaves: list[Leaf] = []
        self.build_tree()
        self.local_scope = {}

    def is_prune(self, element) -> bool:
        for attribute in element.attributes:
            if attribute.name.startswith("n-") or attribute.name.startswith("@") or attribute.name.startswith(":"):
                return True
        return False

    # Peut etre selectionner d'abord les div marquees par un attribut pour alleger le parsing
    # on pourrait faire un attribut zephyr ou autre
    def build_tree(self):
        for html_element in document.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element, {})
                self.leaves.append(leaf)
        print("SUCCES")

    def build_latest_leaves(self, element, local_scope):
        print(element,"ELE?ENT")
        self.local_scope.update(local_scope)
        new_scope = self.local_scope.copy()
        #self.local_scope = new_scope.update(local_scope)
        print("NEW SCOPE", new_scope, local_scope)
        if self.is_prune(element):
                leaf = Leaf(element, new_scope)
                self.latest_leaves.append(leaf)
        for html_element in element.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element, new_scope)
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
                attribute.name.startswith("n-")
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
        print(self.directives)

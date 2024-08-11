from pyscript import document


class Tree:
    def __init__(self) -> None:
        self.leaves: list[Leaf] = []
        self.latest_leaves: list[Leaf] = []
        self.tree_scope: dict[str, any] = {}
        self.build_tree()

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
                leaf = Leaf(html_element)
                self.leaves.append(leaf)


class Leaf:
    def __init__(self, html_element) -> None:
        self.html_element = html_element
        self.directives: dict[str, str] = {}
        self.initial_html_classes = self.html_element.classList.value
        self.initial_n_for_content = None
        self.local_scope = {}
        self.find_directives()

    def get_prune_attributes(self) -> list[str]:
        print([
            attribute.name
            for attribute in self.html_element.attributes
            if (
                attribute.name.startswith("n-")
                or attribute.name.startswith("@")
                or attribute.name.startswith(":")
            )
        ])
        return [
            attribute.name
            for attribute in self.html_element.attributes
            if (
                attribute.name.startswith("n-")
                or attribute.name.startswith("@")
                or attribute.name.startswith(":")
            )
        ]

    def replace_iteration_variable(self, iteration_name, list_name):
        print(self.directives)
        for attribute in self.get_prune_attributes():
            new_value = self.html_element.getAttribute(attribute).replace(
                iteration_name, list_name
            )
            self.directives[attribute] = new_value
            # Inutile mais plus clair dans l'html
            self.html_element.setAttribute(attribute, new_value)
            pass
        pass

    def find_directives(self):
        for directive in self.get_prune_attributes():
            if (
                attribute_value := self.html_element.getAttribute(directive)
            ) is not None:
                self.directives[directive] = attribute_value
        print(self.directives)

from pyscript import document


class Tree:
    def __init__(self) -> None:
        self.leaves: list[Leaf] = []
        self.tree_scope: dict[str, any] = {}
        self.build_tree()

    def is_prune(self, element) -> bool:
        for attribute in element.attributes:
            if attribute.name.startswith("n-"):
                return True
        return False

    # Peut etre selectionner d'abord les div marquees par un attribut pour alleger le parsing
    # on pourrait faire un attribut zephyr ou autre
    def build_tree(self):
        print("BUILD")
        for html_element in document.getElementsByTagName("*"):
            if self.is_prune(html_element):
                leaf = Leaf(html_element)
                self.leaves.append(leaf)
        #self.mutate_dom()

    def mutate_dom(self ):
        print("MUTATE")
        for leaf in self.leaves:
            leaf_scope = leaf.render(self.tree_scope)
            if len(leaf_scope) != 0:
                self.tree_scope.update(leaf_scope)


class Leaf:
    def __init__(self, html_element) -> None:
        self.html_element = html_element
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

   

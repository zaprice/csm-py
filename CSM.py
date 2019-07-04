from typing import Dict, List
from itertools import product


class CSM:
    def __init__(self, prize=0, nx_tree=None, nx_node=0):
        # Prize for taking this node
        self.prize = prize
        # children is a mapping from child nodes to their edge costs
        self.children: Dict["CSM", int] = dict()

        # If given a networkx digraph, import children from there
        # Expects costs as "c" attribute on edges
        # And prizes as "p" attribute on vertices
        if nx_tree is not None:
            self.children = dict(
                zip(
                    [
                        CSM(
                            prize=nx_tree.nodes[child]["p"],
                            nx_tree=nx_tree,
                            nx_node=child,
                        )
                        for child in nx_tree[nx_node]
                    ],
                    [nx_tree[nx_node][child]["c"] for child in nx_tree[nx_node]],
                )
            )

    # Get only child nodes, not edge weights
    def get_children(self) -> List["CSM"]:
        return list(self.children.keys())


# Get all subtrees of the rooted tree "root"
def all_subtrees(root: CSM) -> List[List[CSM]]:
    # leaf
    if len(root.get_children()) == 0:
        return [[root]]
    else:
        # All subtrees from all children
        # Each child gives a List[List[CSM]] of trees from its children
        # So we sum to flatten into List[List[CSM]]
        child_trees: List[List[CSM]] = sum(
            [all_subtrees(child) for child in root.get_children()], []
        )
        # Some subtrees are child trees + the root
        # Some are combinations of child trees + the root
        return all_combos(root, root.get_children(), child_trees)


# All possible combinations of root + some child trees are subtrees
# This is equivalent to taking the product
def all_combos(
    root: CSM, children: List[CSM], child_trees: List[List[CSM]]
) -> List[List[CSM]]:

    # List of their trees for each child
    # Also want to include the empty subtree, as product does not need to pick
    # one from every child
    # Could just be a List[List[List[CSM]]] but the Dict is easier to read
    tree_dict: Dict[CSM, List[List[CSM]]] = dict(
        zip(
            children,
            [
                [tree for tree in child_trees if tree[0] == child] + [[]]
                for child in children
            ],
        )
    )

    # Take product of these lists: one subtree from each child, including empty subtree
    # Concatenate a list of subtrees together with the root, to form a new tree
    return [
        [root] + sum(some_subtrees, [])
        for some_subtrees in product(*tree_dict.values())
    ]

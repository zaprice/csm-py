import networkx as nx

# For typing
from typing import List
from networkx.classes.digraph import DiGraph


class CSM:

    # Optional nx_tree argument to build a CSM from a networkx DiGraph
    # Adds children recursively; nx_curr_node is the index of the current node
    # within the DiGraph object
    def __init__(
        self,
        prize: int = 0,
        cost: int = 0,
        nx_tree: DiGraph = None,
        nx_curr_node: int = 0,
    ):
        # Prize for taking this node
        self.prize: int = prize
        # Cost to take this node
        self.cost: int = cost
        self.children: List["CSM"] = []

        # If given a networkx digraph, import children from there
        # Expects costs as "c" attribute on edges
        # And prizes as "p" attribute on vertices
        if nx_tree is not None:
            self.children = [
                CSM(
                    # Get the prize from the child vertex
                    prize=nx_tree.nodes[child].get("p"),
                    # Get the cost from the edge between this and child
                    cost=nx_tree[nx_curr_node][child].get("c"),
                    nx_tree=nx_tree,
                    nx_curr_node=child,
                )
                for child in nx_tree[nx_curr_node]
            ]

    # Get all nodes of the tree
    def all_nodes(self) -> List["CSM"]:
        return [self] + sum([child.all_nodes() for child in self.children], [])

    # Turns a CSM into a networkx DiGraph
    def csm_2_nx(self) -> DiGraph:
        nodes = self.all_nodes()
        g = nx.DiGraph()

        # Add nodes with prizes
        for n in range(len(nodes)):
            g.add_node(n)
            g.nodes[n]["p"] = nodes[n].prize
            # Add edges
            for child in nodes[n].children:
                child_idx = nodes.index(child)
                g.add_edge(n, child_idx)
                g[n][child_idx]["c"] = child.cost
        return g

    # Returns true if this CSM is iso to the input
    def is_iso(self, target: "CSM") -> bool:
        this_tree: DiGraph = self.csm_2_nx()
        that_tree: DiGraph = target.csm_2_nx()

        # Helper functions defining equality of costs, prizes
        def prize_eq(this_node, that_node):
            return this_node.get("p") == that_node.get("p")

        def cost_eq(this_edge, that_edge):
            return this_edge.get("c") == that_edge.get("c")

        return nx.is_isomorphic(
            this_tree, that_tree, node_match=prize_eq, edge_match=cost_eq
        )

    # Returns this tree's depth-first canonical form
    # From Chi, Yang, Muntz (2004)
    def canonical_form(self) -> str:
        # Backtracking (end-of-branch) char
        back = "$"
        # Representation of this node
        node_rep = f"({self.cost},{self.prize})"

        # leaf
        if not self.children:
            return node_rep + back
        else:
            # Sort forms from children
            child_forms = [child.canonical_form() for child in self.children]
            child_forms.sort(reverse=True)
            return node_rep + "".join(child_forms) + back

    # Faster is_iso based on the canonical form
    def fast_is_iso(self, target: "CSM") -> bool:
        return self.canonical_form() == target.canonical_form()

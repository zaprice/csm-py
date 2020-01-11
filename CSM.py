from typing import List, Tuple
from itertools import product, permutations
from copy import deepcopy

from lib import pairwise

# For typing
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

    # Return the largest prize attainable at each budget
    def max_prize_per_budget(self, subtrees) -> List[int]:
        costs = subtree_costs(subtrees)
        prizes = subtree_prizes(subtrees)
        return prize_per_cost(costs, prizes)


# Get all subtrees of the rooted tree "root"
def all_subtrees(root: CSM) -> List[List[CSM]]:
    # leaf
    if len(root.children) == 0:
        return [[root]]
    else:
        # All subtrees from all children
        # Each child gives a List[List[CSM]] of trees from its children
        # So we sum to flatten into List[List[CSM]]
        child_trees: List[List[CSM]] = sum(
            [all_subtrees(child) for child in root.children], []
        )
        # Some subtrees are child trees + the root
        # Some are combinations of child trees + the root
        return all_combos(root, root.children, child_trees)


# All possible combinations of root + some child trees are subtrees
# This is equivalent to taking the product
def all_combos(
    root: CSM, children: List[CSM], child_trees: List[List[CSM]]
) -> List[List[CSM]]:

    # List of their trees for each child
    # Also want to include the empty subtree, as product does not need to pick
    # one from every child
    tree_list: List[List[List[CSM]]] = [
        [tree for tree in child_trees if tree[0] == child] + [[]] for child in children
    ]

    # Take product of these lists: one subtree from each child, including empty subtree
    # Concatenate a list of subtrees together with the root, to form a new tree
    return [[root] + sum(some_subtrees, []) for some_subtrees in product(*tree_list)]


# Returns total cost of taking subtree, for all subtrees
def subtree_costs(subtrees: List[List[CSM]]) -> List[int]:
    return [sum([node.cost for node in subtree]) for subtree in subtrees]
    # return map(lambda subtree: sum([node.cost for node in subtree]), subtrees)


# Returns total prize in subtree, for all subtrees
def subtree_prizes(subtrees: List[List[CSM]]) -> List[int]:
    return [sum([node.prize for node in subtree]) for subtree in subtrees]


# Given costs, prizes for same subtrees,
# gives best prize for every budget up to max_cost
def prize_per_cost(costs: List[int], prizes: List[int]) -> List[int]:
    # Sort pairs so we only have to loop once
    # Faster to sort in-place
    cost_prize_sort = list(zip(costs, prizes))
    cost_prize_sort.sort(key=lambda pair: pair[0])
    unique_costs = sorted(set(costs))

    # List will be of length max_cost, and will contain the
    # largest prize attainable at that cost
    max_list = []
    i = 0
    curr_max_prize = -1
    # For each unique cost, find the maximum prize
    # Max for everything up to that cost, as curr_max_prize is not reset in the loop
    for (cost, next_cost) in pairwise(unique_costs):
        # Loop until observed cost is greater than current cost
        # We can do this because they are sorted
        # If so, compare to max and continue
        while cost_prize_sort[i][0] <= cost:
            curr_max_prize = max(curr_max_prize, cost_prize_sort[i][1])
            i += 1
        # Add prize to list for each budget between this one and the next
        max_list.extend([curr_max_prize] * (next_cost - cost))
    # Append final prize
    max_list.append(cost_prize_sort[-1][1])
    return max_list


# Get all possible (size n-1) cost and prize labelings of the (size n) input tree
# Given that they are processed one at a time, we don't need to copy
def all_labelings(root: CSM, costs: List[int], prizes: List[int]):
    for cs, ps in product(permutations(costs), permutations(prizes)):
        yield (cs, ps)


# Return all labelings with minimal area under prize-budget curve
def best_labeling(root: CSM, costs: List[int], prizes: List[int]) -> List[CSM]:
    # Copy first so we don't alter the original
    root = deepcopy(root)
    # Get pointers to nodes of the tree
    nodes = root.all_nodes()
    # Can compute subtrees ahead of time, as they are lists of pointer to nodes
    # The nodes get re-labeled every time in the following loop
    subtrees = all_subtrees(root)

    labelings: List[Tuple[List[int], List[int]]] = []
    # List of prize-budget curves for each labeling
    prize_budget_curves: List[List[int]] = []

    # Loop over labelings from all_labelings
    # TODO: we can replace all_labelings with a cleverer version
    for labeling in all_labelings(root, costs, prizes):
        # Apply prize and cost labels to root, via nodes
        apply_labeling(nodes, labeling[0], labeling[1])
        # Store a reference to this labeling
        labelings.append(labeling)
        # Compute the prize-budget curve for this labeling
        prize_budget_curves.append(root.max_prize_per_budget(subtrees))

    # Sum prizes at each budget to get area under the curve
    areas = [sum(prizes) for prizes in prize_budget_curves]
    # min_area is the "optimal" value
    min_area = min(areas)
    # Find which labelings are optimal
    optimal_idxs = [i for i, x in enumerate(areas) if x == min_area]
    unique_optimal_labelings = list({labelings[i] for i in optimal_idxs})

    # Construct a labeled graph for each optimal labeling and return
    graphs = [deepcopy(root) for i in unique_optimal_labelings]
    for i in range(len(graphs)):
        apply_labeling(
            graphs[i].all_nodes(),
            unique_optimal_labelings[i][0],
            unique_optimal_labelings[i][1],
        )
    return graphs


def apply_labeling(nodes: List[CSM], costs: List[int], prizes: List[int]) -> None:
    for i in range(len(prizes)):
        nodes[i + 1].cost = costs[i]
        nodes[i + 1].prize = prizes[i]

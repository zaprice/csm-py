from typing import List
from itertools import product, permutations

from lib import pairwise


class CSM:
    def __init__(self, prize=0, cost=0, nx_tree=None, nx_node=0):
        # Prize for taking this node
        self.prize = prize
        # Cost to take this node
        self.cost = cost
        self.children: List["CSM"] = []

        # If given a networkx digraph, import children from there
        # Expects costs as "c" attribute on edges
        # And prizes as "p" attribute on vertices
        if nx_tree is not None:
            self.children = [
                CSM(
                    prize=nx_tree.nodes[child]["p"],
                    cost=nx_tree[nx_node][child]["c"],
                    nx_tree=nx_tree,
                    nx_node=child,
                )
                for child in nx_tree[nx_node]
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
    nodes = root.all_nodes()
    for cs, ps in product(permutations(costs), permutations(prizes)):
        for i in range(len(ps)):
            nodes[i + 1].prize = ps[i]
            nodes[i + 1].cost = cs[i]
        yield root

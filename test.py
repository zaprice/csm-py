import unittest
from functools import reduce
from math import factorial

from CSM import CSM, all_subtrees, subtree_costs, subtree_prizes, all_labelings
from nx_tree import zero_csm, random_csm


# Return the largest prize attainable at each budget
# Simpler version for testing against CSM.max_prize_per_budget
def max_prize_per_budget(root):
    subtrees = all_subtrees(root)
    costs = subtree_costs(subtrees)
    prizes = subtree_prizes(subtrees)
    max_budget = max(costs)

    cost_prize = list(zip(costs, prizes))

    # Slow, loops over (n_subtrees) list max_budget times
    return [
        max([pair[1] for pair in cost_prize if pair[0] <= n])
        for n in range(max_budget + 1)
    ]


class TestCSM(unittest.TestCase):

    # Assert that the tree and CSM have the same number of children from each node
    def num_children(self, tree, tree_node, c):
        self.assertEqual(len(tree[tree_node]), len(c.children))
        [
            self.num_children(tree, pair[0], pair[1])
            for pair in zip(tree[tree_node], c.children)
        ]

    # Assert that the tree and CSM have the same costs
    def check_costs(self, tree, tree_node, parent, c):
        if parent is not None:
            self.assertEqual(tree[parent][tree_node]["c"], c.cost)
        [
            self.check_costs(tree, pair[0], tree_node, pair[1])
            for pair in zip(tree[tree_node], c.children)
        ]

    # Assert that the tree and CSM have the same prizes
    def check_prizes(self, tree, tree_node, c):
        if tree_node != 0:
            self.assertEqual(tree.nodes[tree_node]["p"], c.prize)
        [
            self.check_prizes(tree, pair[0], pair[1])
            for pair in zip(tree[tree_node], c.children)
        ]

    def testInitZero(self):
        for n in range(1, 50):
            tree = zero_csm(n)
            self.num_children(tree, 0, CSM(nx_tree=tree))

    def testInitRandom(self):
        for n in range(1, 50):
            tree = random_csm(n)
            self.num_children(tree, 0, CSM(nx_tree=tree))
            self.check_costs(tree, 0, None, CSM(nx_tree=tree))
            self.check_prizes(tree, 0, CSM(nx_tree=tree))

    def testMaxPrize(self):
        for n in range(1, 30):
            c = CSM(nx_tree=random_csm(n))
            ppb = c.max_prize_per_budget(all_subtrees(c))
            self.assertEqual(ppb, max_prize_per_budget(c))
            # Prizes must be increasing
            self.assertTrue(
                reduce(
                    lambda bool, pair: bool and pair[0] <= pair[1],
                    zip(ppb, ppb[1:]),
                    True,
                )
            )

    def testLabelings(self):
        for n in range(1, 7):
            c = CSM(nx_tree=random_csm(n))
            # Make sure there are the expected (n-1)!^2 labelings
            n_labelings = sum(1 for l in all_labelings(c, [0] * (n - 1), [0] * (n - 1)))
            self.assertEqual(n_labelings, factorial(n - 1) ** 2)

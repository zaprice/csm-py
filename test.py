import unittest
from functools import reduce
from math import factorial
from copy import deepcopy

from CSM import CSM
from optimal import all_subtrees, subtree_costs, subtree_prizes, max_prize_per_budget
from labeler import all_labelings
from nx_tree import zero_csm, random_csm


# Return the largest prize attainable at each budget
# Simpler version for testing against CSM.max_prize_per_budget
def max_prize_per_budget_alt(root):
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

    def test_init_zero(self):
        for n in range(1, 50):
            tree = zero_csm(n, mine=False)
            self.num_children(tree, 0, CSM(nx_tree=tree))

    def test_init_random(self):
        for n in range(1, 50):
            tree = random_csm(n, mine=False)
            self.num_children(tree, 0, CSM(nx_tree=tree))
            self.check_costs(tree, 0, None, CSM(nx_tree=tree))
            self.check_prizes(tree, 0, CSM(nx_tree=tree))

    def test_max_prize(self):
        for n in range(1, 30):
            c = CSM(nx_tree=random_csm(n, mine=False))
            ppb = max_prize_per_budget(c, all_subtrees(c))
            self.assertEqual(ppb, max_prize_per_budget_alt(c))
            # Prizes must be increasing
            self.assertTrue(
                reduce(
                    lambda bool, pair: bool and pair[0] <= pair[1],
                    zip(ppb, ppb[1:]),
                    True,
                )
            )

    def test_labelings(self):
        for n in range(1, 7):
            c = CSM(nx_tree=random_csm(n))
            # Make sure there are the expected (n-1)!^2 labelings
            n_labelings = sum(
                1 for l in all_labelings(c, list(range(n - 1)), list(range(n - 1)))
            )
            self.assertEqual(n_labelings, factorial(n - 1) ** 2)

    def test_isomorphism(self):
        # Test is_iso and fast_is_iso
        for n in range(2, 10):
            c = CSM(nx_tree=random_csm(n))
            # c iso to itself, and to a copy of itself
            self.assertTrue(c.is_iso(c))
            self.assertTrue(c.is_iso(deepcopy(c)))
            self.assertTrue(c.fast_is_iso(c))
            self.assertTrue(c.fast_is_iso(deepcopy(c)))
            # Not iso if you change a vertex or edge label
            d = deepcopy(c)
            d.children[0].prize += 1
            self.assertFalse(c.is_iso(d))
            self.assertFalse(c.fast_is_iso(d))
            d = deepcopy(c)
            d.children[0].cost += 1
            self.assertFalse(c.is_iso(d))
            self.assertFalse(c.fast_is_iso(d))

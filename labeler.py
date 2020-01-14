from itertools import product
from CSM import CSM
from sympy.utilities.iterables import multiset_permutations

from typing import List, Tuple, Iterator


# Get all possible (size n-1) cost and prize labelings of the (size n) input tree
# Given that they are processed one at a time, we don't need to copy
def all_labelings(
    root: CSM, costs: List[int], prizes: List[int]
) -> Iterator[Tuple[List[int], List[int]]]:
    # Use multiset permutations to account for possible duplicates in costs/prizes
    for cs, ps in product(m_perms(costs), m_perms(prizes)):
        yield (cs, ps)


# Needed to replicate behavior of itertools.permutations([])
def m_perms(l: List):
    if l:
        return multiset_permutations(l)
    else:
        return [()]

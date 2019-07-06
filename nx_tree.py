import networkx as nx
import matplotlib.pyplot as plt
import random

# Set same seed for testing
random.seed(1)


# Draw the networkx graph g
# Only works in ipython
def draw(g):
    plt.subplot(121)
    nx.draw(g, with_labels=True, font_weight="bold")


# Generate a random rooted tree on n vertices
# as a networkx digraph
def random_rooted_tree(n):
    # Node 0 is the root
    # Graph starts out with all bidirectional edges
    di_g = nx.random_tree(n).to_directed()
    # Remove edges pointing towards the root
    to_directed_tree(di_g)
    return di_g


# Convert di_g to a directed rooted tree
# by removing all edges pointing towards 0
def to_directed_tree(di_g):
    to_directed_tree_recur(di_g, 0)


def to_directed_tree_recur(di_g, node):
    children = di_g[node]
    if len(children) != 0:
        for child in children:
            di_g.remove_edge(child, node)
            to_directed_tree_recur(di_g, child)


# Generate a random cyber-security model on n vertices
# aka a rooted tree with random edge and vertex labels (costs and prizes)
def random_csm(n):
    tree = random_rooted_tree(n)
    # Label non-root vertices with prizes as the attribute 'p'
    prize_mapping = dict(zip(range(1, n), random_c_or_p(n)))
    for k, p in prize_mapping.items():
        tree.nodes[k]["p"] = p
    # Label edges with costs as the attribute 'c'
    cost_mapping = dict(zip(tree.edges, random_c_or_p(n)))
    for (inv, outv), c in cost_mapping.items():
        tree[inv][outv]["c"] = c
    return tree


# Generate a random tree cyber-security model on n vertices
# with 0 prize/cost for every vertex/edge
def zero_csm(n):
    tree = random_rooted_tree(n)
    for k in range(1, n):
        tree.nodes[k]["p"] = 0
    for inv, outv in tree.edges:
        tree[inv][outv]["c"] = 0
    return tree


def random_c_or_p(n):
    return [random.randint(1, 10) for i in range(n)]

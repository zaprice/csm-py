import networkx as nx
import matplotlib.pyplot as plt


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

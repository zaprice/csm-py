import networkx as nx
import matplotlib.pyplot as plt
import random

from CSM import CSM

# Set same seed for testing
random.seed(1)


# Draw the networkx graph g
# Only works in ipython
def draw(g):
    plt.subplot(121)
    nx.draw(g, with_labels=True, font_weight="bold")


# Convert CSM back to networkx so we can draw it
def draw_csm(root: CSM):
    g = csm_2_nx(root)
    node_labels = dict(
        zip(range(len(root.all_nodes())), [node.prize for node in root.all_nodes()])
    )

    edge_labels = dict(zip(g.edges, [g[edge[0]][edge[1]]["c"] for edge in g.edges]))
    layout = nx.shell_layout(g)
    nx.draw(g, pos=layout, labels=node_labels, edge_labels=edge_labels)
    nx.draw_networkx_edge_labels(g, layout, edge_labels=edge_labels)


# Generate a random rooted tree on n vertices
# as a networkx digraph
def random_rooted_tree(n, mine=True):
    # Node 0 is the root
    if mine:
        # Tends to produce a wider, shorter tree
        di_g = my_random_rooted_tree(n)
    else:
        # Tends to produce a taller, skinnier tree
        # Graph starts out with all bidirectional edges
        di_g = nx.random_tree(n).to_directed()
        # Remove edges pointing towards the root
        di_g = to_directed_tree(di_g)
    return di_g


def my_random_rooted_tree(n):
    g = nx.DiGraph()
    # Node 0 is the root
    nodes = range(n)
    for i in nodes:
        g.add_node(i)

    remaining_edges = n - 1
    # For each node, roll for # of children
    for i in nodes:
        if remaining_edges > 0:
            if remaining_edges == 1:
                n_children = 1
            else:
                n_children = random.randint(1, remaining_edges)
            # Connect those children and move to the next node
            for k in range(n - remaining_edges, n - remaining_edges + n_children):
                g.add_edge(i, k)
            remaining_edges -= n_children
        else:
            return g
    return g


# Convert di_g to a directed rooted tree
# by removing all edges pointing towards 0
def to_directed_tree(di_g):
    to_directed_tree_recur(di_g, 0)
    return di_g


def to_directed_tree_recur(di_g, node):
    children = di_g[node]
    if len(children) != 0:
        for child in children:
            di_g.remove_edge(child, node)
            to_directed_tree_recur(di_g, child)


# Generate a random cyber-security model on n vertices
# aka a rooted tree with random edge and vertex labels (costs and prizes)
def random_csm(n, mine=True):
    tree = random_rooted_tree(n, mine)
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
def zero_csm(n, mine=True):
    tree = random_rooted_tree(n, mine)
    for k in range(1, n):
        tree.nodes[k]["p"] = 0
    for inv, outv in tree.edges:
        tree[inv][outv]["c"] = 0
    return tree


def random_c_or_p(n):
    return [random.randint(1, 10) for i in range(n)]


def csm_2_nx(root: CSM):
    nodes = root.all_nodes()
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

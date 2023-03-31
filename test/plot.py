import networkx as nx
import matplotlib.pyplot as plt


def plot_graph(graph: nx.classes.DiGraph):
    labels = {i: str(type(i)).split('.')[-1][: -2] for i in graph.nodes()}

    nx.draw_networkx(graph, labels=labels)
    plt.show()

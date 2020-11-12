from random import sample, random

from network.graph import Graph


def run_simulation(graph, start, test_broadcast=None,
                   test_edge=None, metadata=None):
    transmission = graph.transmit(start, test_broadcast=test_broadcast,
                                  test_edge=test_edge)
    return Transmission(tuple(transmission), metadata)


def random_graph(n_nodes, param_generator):
    graph = Graph(range(n_nodes))

    for node in graph.nodes:
        edges_to_build = param_generator.follow_count(n_nodes)
        pool = set(graph.nodes)
        pool.remove(node)
        for node_to_follow in sample(pool, edges_to_build):
            graph.add_edge(edge=(node_to_follow, node),
                           strength=param_generator.edge_strength())

    return graph


class Transmission:
    def __init__(self, path, metadata=None):
        if len(path) < 1:
            raise ValueError('Path must be a list or tuple with entries')
        self.path = path
        self._metadata = metadata or {}

    @property
    def originating_node(self):
        return self.path[0].from_node

    @property
    def metadata(self):
        return dict(self._metadata)


def test(p):
    assert 0 <= p <= 1
    return random() < p

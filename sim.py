from random import choice, sample, random

from graph import Graph


class Simulation:
    @classmethod
    def create(cls, n_nodes, param_generator):
        graph = Graph(range(n_nodes))
        sim = cls(graph, param_generator)
        sim.initialize()
        return sim

    def __init__(self, graph, param_generator):
        self.graph = graph
        self.param_generator = param_generator
        self.step_index = 0

    def initialize(self, param_generator=None):
        if param_generator is not None:
            self.param_generator = param_generator
        graph_size = len(self.graph.nodes)
        for node in self.graph.nodes:
            self._build_edges(node, n=self.param_generator.follow_count(graph_size))
        # for node in self.graph.nodes:
        #     self._evaluate_edges(node)

    def _build_edges(self, node, n):
        if n >= len(self.graph.nodes):
            raise ValueError(f'Not enough nodes in graph to build {n} edges')
        pool = set(self.graph.nodes)
        pool.remove(node)
        for node_to_follow in sample(pool, n):
            self.graph.add_edge(edge=(node, node_to_follow),
                                strength=self.param_generator.edge_strength())

    def _evaluate_edges(self, node, symmetric_edges=True):
        conns = next(self.graph.children(node))
        for conn in conns:
            if test(self.param_generator.p_follow_back()) and not self.graph.contains_edge((conn, node)):
                if symmetric_edges:
                    new_edge_strength = self.graph.get_edge_attrs((node, conn))['strength']
                else:
                    new_edge_strength = self.param_generator.edge_strength()
                self.graph.add_edge(edge=(conn, node), strength=new_edge_strength)

    def step(self, p_rebroadcast=None, originating_node=None):
        if p_rebroadcast is None:
            p_rebroadcast = self.param_generator.p_rebroadcast()
        if originating_node is None:
            originating_node = choice(list(self.graph.nodes))

        result = tuple(
            self.graph.transmit(originating_node,
                                test_broadcast=lambda node: test(p_rebroadcast),
                                test_edge=lambda edge: test(edge.strength))
        )
        return Transmission(self.step_index, result, p_rebroadcast=p_rebroadcast)

    def run(self, n, **kw):
        return [self.step(**kw) for _ in range(n)]


class Transmission:
    def __init__(self, id, nodes, **metadata):
        self.id = id
        self.nodes = nodes
        self.originating_node = nodes[0]
        self.metadata = metadata


def test(p):
    assert 0 <= p <= 1
    return random() < p

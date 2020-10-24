from random import choice, sample

from graph import Graph
from helpers import test


class Simulation:
    @classmethod
    def create(cls, n_nodes, param_generator):
        graph = Graph()
        for i in range(n_nodes):
            graph.add_empty_node(i)
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
        for node in self.graph.nodes:
            self._evaluate_edges(node)

    def _build_edges(self, node, n):
        if n > len(self.graph.nodes):
            raise ValueError(f'Not enough nodes in graph to build {n} edges')
        for node_to_follow in sample(self.graph.nodes, n):
            self.graph.add_edge(connection=(node, node_to_follow),
                                strength=self.param_generator.edge_strength())

    def _evaluate_edges(self, node):
        conns, = self.graph.connections(node)
        for conn in conns:
            if test(self.param_generator.p_follow_back()) and not self.graph.contains((node, conn)):
                self.graph.add_edge(connection=(conn, node),
                                    strength=self.param_generator.edge_strength())

    def step(self, p_rebroadcast=None, originating_node=None):
        if p_rebroadcast is None:
            p_rebroadcast = self.param_generator.p_rebroadcast()
        if originating_node is None:
            originating_node = choice(list(self.graph.nodes))

        msg = Message(self.step_index, p_rebroadcast, originating_node)
        self.graph.submit(msg)
        self.step_index += 1
        return msg

    def run(self, n, **kw):
        msgs = [self.step(**kw) for _ in range(n)]
        return msgs


class Message:
    def __init__(self, id, p_rebroadcast, originating_node):
        self.id = id
        self.p_rebroadcast = p_rebroadcast
        self.broadcasted_nodes = set()
        self.originating_node = originating_node

    def is_broadcasted_by(self, node):
        return node in self.broadcasted_nodes

    def track_broadcast_by(self, node):
        self.broadcasted_nodes.add(node)

    def __str__(self):
        return f'<Message, id: {self.id} broadcasted by {len(self.broadcasted_nodes)} nodes>'

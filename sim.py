from collections import namedtuple
from random import random, choice, sample

DEBUG = False


def trace(thing):
    if DEBUG:
        print(thing)


def test(p):
    assert 0 <= p <= 1
    return random() < p


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


_Edge = namedtuple('Edge', ['to', 'strength'])


class _Queue:
    def __init__(self):
        self._items = []
        self._init_index = 0

    def empty(self):
        return self._init_index >= len(self._items)

    def add(self, item):
        self._items.append(item)

    def remove(self):
        item = self._items[self._init_index]
        self._init_index += 1
        return item


class Graph:
    def __init__(self):
        self._nodes = {}

    @property
    def nodes(self):
        return self._nodes.keys()

    def add_empty_node(self, index):
        self._nodes[index] = set()

    def contains(self, connection):
        from_node, _ = connection
        if from_node not in self._nodes:
            return False
        return connection in self._nodes[from_node]

    def add_edge(self, connection, strength):
        if self.contains(connection):
            raise ValueError(f'Connection {connection} already exists')
        from_node, to_node = connection
        if from_node not in self._nodes:
            self.add_empty_node(from_node)
        new_edge = _Edge(to=to_node, strength=strength)
        self._nodes[from_node].add(new_edge)

    def submit(self, msg):
        if msg.originating_node not in self._nodes:
            raise ValueError(f'Invalid originating node {msg.originating_node} for msg')
        queue = _Queue()
        queue.add(msg.originating_node)

        while not queue.empty():
            node_index = queue.remove()
            msg.track_broadcast_by(node_index)
            for edge in self._nodes[node_index]:
                ack = test(edge.strength)
                rebroadcast = not msg.is_broadcasted_by(edge.to) and test(msg.p_rebroadcast)
                if ack and rebroadcast:
                    queue.add(edge.to)
        return msg

    def _get_connections_for(self, node_index, predicate):
        edges = self._nodes[node_index]
        if not predicate:
            predicate = lambda node: True
        return [edge.to for edge in edges if predicate(edge.to)]

    def connections(self, node_index, deg=1, predicate=None):
        if node_index not in self._nodes:
            raise ValueError(f'Node {node_index} not in this graph')
        if deg < 1:
            raise ValueError('Deg must be >= 1')

        deg_on = 1
        tracked_conns = self._get_connections_for(node_index, predicate)
        traversed_nodes = set(tracked_conns)
        result = [tuple(tracked_conns)]

        while deg_on < deg:
            this_deg_conns = []
            for tracked_conn in tracked_conns:
                next_conns = [conn for conn in self._get_connections_for(tracked_conn, predicate)
                              if conn not in traversed_nodes]
                traversed_nodes.update(next_conns)
                this_deg_conns += next_conns
            deg_on += 1
            result.append(tuple(this_deg_conns))
            tracked_conns = this_deg_conns

        return tuple(result)


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

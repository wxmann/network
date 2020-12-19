import attr
from typing import Any


@attr.s(frozen=True, slots=True)
class _Edge:
    from_node: Any = attr.ib()
    to_node: Any = attr.ib()
    attrs: dict = attr.ib(factory=dict, eq=False, repr=False, order=False)
    nodes: tuple = attr.ib(
        init=False, eq=False, repr=False, order=False,
        default=attr.Factory(
            lambda self: (self.from_node, self.to_node),
            takes_self=True
        )
    )

    def attr(self, item):
        return self.attrs.get(item, None)


class Graph:
    @classmethod
    def of_size(cls, n_nodes, directed):
        return cls(vertices=range(n_nodes), directed=directed)

    @classmethod
    def duplicate(cls, graph):
        inst = cls(graph.nodes, graph.directed)
        for edge in graph.iter_edges():
            if not inst.contains_edge(edge):
                inst.add_edge(edge.nodes, **edge.attrs)
        return inst

    def __init__(self, vertices=None, directed=True):
        if vertices is None:
            vertices = []
        self._A = {vertex: {} for vertex in vertices}
        self._directed = directed

    @property
    def nodes(self):
        return self._A.keys()

    @property
    def num_edges(self):
        num = sum(len(edges) for edges in self._A.values())
        return num if self._directed else num / 2

    @property
    def directed(self):
        return self._directed

    def iter_edges(self):
        traversed_edges = set()
        for from_node in self._A:
            for to_node in self._A[from_node]:
                if self._directed:
                    yield self._get_edge((from_node, to_node))
                elif (to_node, from_node) not in traversed_edges:
                    traversed_edges.add((from_node, to_node))
                    yield self._get_edge((from_node, to_node))

    def contains_node(self, node):
        return node in self._A

    def _get_edge(self, edge):
        from_node, to_node = Graph._nodes_of(edge)
        attrs = self._A[from_node][to_node]
        return _Edge(from_node, to_node, dict(attrs))

    def contains_edge(self, edge):
        from_node, to_node = Graph._nodes_of(edge)
        return from_node in self._A and to_node in self._A[from_node]

    @staticmethod
    def _nodes_of(edge):
        if isinstance(edge, _Edge):
            return edge.nodes
        return edge

    def add_node(self, node):
        if self.contains_node(node):
            raise ValueError(f'Graph already contains node {node}')
        self._A[node] = {}

    def add_edge(self, edge, **attrs):
        if self.contains_edge(edge):
            raise ValueError(f'Edge {edge} already exists')
        from_node, to_node = edge

        if not self.contains_node(from_node):
            self._A[from_node] = {}
        if not self.contains_node(to_node):
            self._A[to_node] = {}

        self._A[from_node][to_node] = attrs
        if not self._directed:
            self._A[to_node][from_node] = attrs

    def remove_edge(self, edge):
        if self.contains_edge(edge):
            from_node, to_node = Graph._nodes_of(edge)
            edge = self._A[from_node][to_node]
            del self._A[from_node][to_node]

            if not self._directed:
                edge2 = self._A[to_node][from_node]
                del self._A[to_node][from_node]
                return edge, edge2
            else:
                return edge
        return None

    def update_edge(self, edge, **attrs):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        from_node, to_node = Graph._nodes_of(edge)
        self._A[from_node][to_node].update(attrs)
        if not self._directed:
            self._A[to_node][from_node].update(attrs)

    def get_edge_attrs(self, edge):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        return dict(self._get_edge(edge).attrs)

    def _children_for(self, node_index, predicate=None):
        return (node for node in self._A[node_index]
                if predicate is None or predicate(node))

    def children(self, node_index, deg=1, predicate=None, exclude_dups=True):
        if not self.contains_node(node_index):
            raise ValueError(f'Node {node_index} does not exist in this graph')
        if deg is not None and deg < 1:
            raise ValueError('Deg must be >= 1')

        deg_on = 1
        tracked_deg_nodes = list(self._children_for(node_index, predicate))
        traversed_nodes = set(tracked_deg_nodes)
        traversed_nodes.add(node_index)
        yield tracked_deg_nodes

        while deg is None or deg_on < deg:
            deg_on += 1
            this_deg_nodes = []
            for parent in tracked_deg_nodes:
                is_dup = lambda node: exclude_dups and node in traversed_nodes
                this_deg_nodes += [node for node in self._children_for(parent, predicate)
                                   if not is_dup(node)]
                traversed_nodes.update(this_deg_nodes)
            tracked_deg_nodes = this_deg_nodes
            yield tracked_deg_nodes

    def outbound_edges(self, from_node):
        if not self.contains_node(from_node):
            raise ValueError(f'Node {from_node} does not exist in this graph')
        for child in self._children_for(from_node):
            yield self._get_edge((from_node, child))

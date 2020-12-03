class _Edge:
    def __init__(self, from_node, to_node, **kwargs):
        self.from_node = from_node
        self.to_node = to_node
        self._attrs = kwargs

    @property
    def attrs(self):
        return dict(self._attrs)

    @property
    def nodes(self):
        return self.from_node, self.to_node

    # def get(self, item):
    #     return self._attrs.get(item, None)
    #
    def update(self, **kwargs):
        self._attrs.update(kwargs)

    def __getattr__(self, item):
        try:
            return self._attrs[item]
        except KeyError:
            raise AttributeError

    def __hash__(self):
        return hash((self.from_node, self.to_node))

    def __str__(self):
        return f'<Edge from: {self.from_node} to {self.to_node}>'


class Graph:
    _UNDEFINED_NODE = 'EMPTY'

    @classmethod
    def of_size(cls, n_nodes):
        return cls(vertices=range(n_nodes))

    def __init__(self, vertices=None):
        if vertices is None:
            vertices = []
        self._nodes = {vertex: {} for vertex in vertices}

    @property
    def nodes(self):
        return self._nodes.keys()

    @property
    def num_edges(self):
        return sum(len(edges) for edges in self._nodes.values())

    def iter_edges(self):
        for from_node in self._nodes:
            for to_node in self._nodes[from_node]:
                yield self._get_edge((from_node, to_node))

    def contains_node(self, node):
        return node in self._nodes

    def _get_edge(self, edge):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        from_node, to_node = edge
        node_attrs = self._nodes[from_node][to_node]
        return _Edge(from_node, to_node, **node_attrs)

    def contains_edge(self, edge):
        from_node, to_node = edge
        return from_node in self._nodes and to_node in self._nodes[from_node]

    def add_node(self, node):
        if self.contains_node(node):
            raise ValueError(f'Graph already contains node {node}')
        self._nodes[node] = {}

    def add_edge(self, edge, **attrs):
        if self.contains_edge(edge):
            raise ValueError(f'Edge {edge} already exists')
        from_node, to_node = edge

        if not self.contains_node(from_node):
            self._nodes[from_node] = {}

        self._nodes[from_node][to_node] = attrs

        if not self.contains_node(to_node):
            self._nodes[to_node] = {}

    def remove_edge(self, edge):
        if self.contains_edge(edge):
            from_node, to_node = edge
            edge = self._nodes[from_node][to_node]
            del self._nodes[from_node][to_node]
            return edge
        return None

    def update_edge(self, edge, **attrs):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        from_node, to_node = edge
        self._nodes[from_node][to_node].update(attrs)

    def get_edge_attrs(self, edge):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        return self._get_edge(edge).attrs

    def _children_for(self, node_index, predicate=None):
        return (node for node in self._nodes[node_index]
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


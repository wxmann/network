class _Edge:
    def __init__(self, from_node, to_node, **kwargs):
        self.from_node = from_node
        self.to_node = to_node
        self._attrs = kwargs

    @property
    def attrs(self):
        return dict(self._attrs)

    def get(self, item):
        return self._attrs.get(item, None)

    def __getattr__(self, item):
        try:
            return self._attrs[item]
        except KeyError:
            raise AttributeError

    def __str__(self):
        return f'<Edge from: {self.from_node} to {self.to_node}>'


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
    _UNDEFINED_NODE = 'EMPTY'

    def __init__(self, vertices=None):
        if vertices is None:
            vertices = []
        self._nodes = {vertex: {} for vertex in vertices}

    @property
    def nodes(self):
        return self._nodes.keys()

    def iter_edges(self):
        for node, edges in self._nodes.items():
            for edge in edges.values():
                yield edge

    def contains_node(self, node):
        return node in self._nodes

    def _get_edge(self, edge):
        from_node, to_node = edge
        return self._nodes.get(from_node, {}).get(to_node, Graph._UNDEFINED_NODE)

    def contains_edge(self, edge):
        return self._get_edge(edge) is not Graph._UNDEFINED_NODE

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

        new_edge = _Edge(from_node, to_node, **attrs)
        self._nodes[from_node][to_node] = new_edge

        if not self.contains_node(to_node):
            self._nodes[to_node] = {}

    def get_edge_attrs(self, edge):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        return self._get_edge(edge).attrs

    def transmit(self, from_node, test_broadcast=None, test_edge=None):
        if from_node not in self._nodes:
            raise ValueError(f'Node {from_node} does not exist in this graph')
        queue = _Queue()
        nodes_broadcasted = set()

        def do_broadcast(node):
            for child in self._children_for(node):
                queue.add(self._get_edge((node, child)))
                nodes_broadcasted.add(node)

        do_broadcast(from_node)

        while not queue.empty():
            edge = queue.remove()
            if all([
                edge.to_node not in nodes_broadcasted,
                test_edge is None or test_edge(edge),
                test_broadcast is None or test_broadcast(edge.to_node)
            ]):
                yield edge
                do_broadcast(edge.to_node)

    def traverse_edges(self, from_node):
        if from_node not in self._nodes:
            raise ValueError(f'Node {from_node} does not exist in this graph')
        queue = _Queue()
        queue.add(from_node)
        nodes_traversed = set()

        while not queue.empty():
            node = queue.remove()
            if node not in nodes_traversed:
                nodes_traversed.add(node)
                for child in self._children_for(node):
                    yield self._get_edge((node, child))
                    queue.add(child)

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

class _Edge:
    def __init__(self, from_node, to_node, **kwargs):
        self.from_node = from_node
        self.to_node = to_node
        self._attrs = kwargs

    @property
    def attrs(self):
        return dict(self._attrs)

    def __getattr__(self, item):
        try:
            return self._attrs[item]
        except KeyError:
            raise AttributeError


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

    def __init__(self):
        self._nodes = {}

    @property
    def nodes(self):
        return self._nodes.keys()

    @property
    def structure(self):
        return dict(self._nodes)

    def add_standalone_node(self, index):
        self._nodes[index] = {}

    def contains_node(self, node):
        return node in self._nodes

    def _get_edge(self, edge):
        from_node, to_node = edge
        return self._nodes.get(from_node, {}).get(to_node, Graph._UNDEFINED_NODE)

    def contains_edge(self, edge):
        return self._get_edge(edge) is not Graph._UNDEFINED_NODE

    def add_edge(self, edge, **attrs):
        if self.contains_edge(edge):
            raise ValueError(f'Edge {edge} already exists')
        from_node, to_node = edge
        if not self.contains_node(from_node):
            self.add_standalone_node(from_node)
        new_edge = _Edge(from_node, to_node, **attrs)
        self._nodes[from_node][to_node] = new_edge

    def get_edge_attrs(self, edge):
        if not self.contains_edge(edge):
            raise ValueError(f'Edge {edge} does not exist')
        return self._get_edge(edge).attrs

    def bfs_traversal(self, from_node, take=None, skip_traversed=True):
        if not self.contains_node(from_node):
            raise ValueError(f'Node {from_node} does not exist in this graph')
        queue = _Queue()
        queue.add(from_node)
        nodes_traversed = set()

        while not queue.empty():
            node_index = queue.remove()
            nodes_traversed.add(node_index)
            yield node_index

            for to_node, edge in self._nodes[node_index].items():
                skip_dup = to_node in nodes_traversed if skip_traversed else False
                take_edge = take is None or take(edge)
                if take_edge and not skip_dup:
                    queue.add(to_node)

    def _get_connections_for(self, node_index, predicate):
        to_nodes = self._nodes[node_index]
        if not predicate:
            predicate = lambda node: True
        return [to_node for to_node in to_nodes if predicate(to_node)]

    def connections(self, node_index, deg=1, predicate=None):
        if not self.contains_node(node_index):
            raise ValueError(f'Node {node_index} does not exist in this graph')
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

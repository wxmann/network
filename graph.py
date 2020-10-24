from helpers import test


class _Edge:
    def __init__(self, to, **kwargs):
        self.to = to
        self._attrs = kwargs

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
    def __init__(self):
        self._nodes = {}

    @property
    def nodes(self):
        return self._nodes.keys()

    @property
    def structure(self):
        return dict(self._nodes)

    def add_empty_node(self, index):
        self._nodes[index] = set()

    def contains(self, connection):
        from_node, to_node = connection
        if from_node not in self._nodes:
            return False
        to_nodes = set(edge.to for edge in self._nodes[from_node])
        return to_node in to_nodes

    def add_edge(self, connection, strength):
        if self.contains(connection):
            raise ValueError(f'Connection {connection} already exists')
        from_node, to_node = connection
        if from_node not in self._nodes:
            self.add_empty_node(from_node)
        new_edge = _Edge(to_node, strength=strength)
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
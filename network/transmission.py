class GraphTransmission:
    def __init__(self, graph, from_node, selector, test_transmit=None):
        self.graph = graph
        self.originating_node = from_node
        self.test_transmit = test_transmit
        self._selector = selector
        self._nodes_broadcasted = set()
        self._step_index = 0
        self._tests = 0

        self._do_broadcast(self.originating_node)

    @property
    def steps(self):
        return self._step_index

    @property
    def broadcasts(self):
        return len(self._nodes_broadcasted)

    @property
    def tests(self):
        return self._tests

    def __iter__(self):
        return self

    def _do_broadcast(self, node):
        for edge in self.graph.outbound_edges(node):
            self._selector.add(edge)
            self._nodes_broadcasted.add(node)

    def __next__(self):
        self._step_index += 1
        while not self._selector.empty():
            edges = []
            for edge in self._selector.remove():
                if edge.to_node not in self._nodes_broadcasted:
                    self._tests += 1
                    if self.test_transmit is None or self.test_transmit(self, edge):
                        self._do_broadcast(edge.to_node)
                        edges.append(edge)
            return tuple(edges)
        raise StopIteration


# class Selector:
#     def __init__(self, items):
#         self._items = items
#
#     def empty(self):
#         return len(self._items) == 0
#
#     def add(self, item):
#         if isinstance(self._items, list):
#             self._items.append(item)
#         elif isinstance(self._items, set):
#             self._items.add(item)
#         else:
#             raise ValueError('can only ad item to list or set')
#
#     def _pick(self):
#         raise NotImplementedError
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         if self.empty():
#             raise StopIteration
#         return self._pick()


class FIFOSelector:
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
        return item,


class RandomSelector:
    def __init__(self, random=None, n=1):
        import random as default_random
        self._items = set()
        self._random = random or default_random
        self.n = n

    def empty(self):
        return len(self._items) == 0

    def add(self, item):
        self._items.add(item)

    def remove(self):
        if self.empty():
            raise IndexError
        npick = self.n() if callable(self.n) else self.n
        picked = self._random.sample(self._items, min(npick, len(self._items)))
        for item in picked:
            self._items.discard(item)
        return picked


class DelayedSelector:
    def __init__(self, lag):
        self._items = set()
        self.lag = lag
        self._time_counter = 0

    def empty(self):
        return len(self._items) == 0

    def add(self, item):
        lag_time = self.lag() if callable(self.lag) else self.lag
        item = (self._time_counter, lag_time, item)
        self._items.add(item)

    def remove(self):
        if self.empty():
            raise IndexError
        items_to_pick = [item for (t0, dt, item) in self._items
                         if self._time_counter == t0 + dt]
        for item_to_remove in items_to_pick:
            self._items.discard(item_to_remove)
        self._time_counter += 1
        return items_to_pick

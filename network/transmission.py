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
        edges = []
        for edge in next(self._selector):
            if edge.to_node not in self._nodes_broadcasted:
                self._tests += 1
                if self.test_transmit is None or self.test_transmit(self, edge):
                    self._do_broadcast(edge.to_node)
                    edges.append(edge)
        return tuple(edges)


class Selector:
    def __init__(self, items):
        self._items = items

    def empty(self):
        return len(self._items) == 0

    def add(self, item):
        if isinstance(self._items, list):
            self._items.append(item)
        elif isinstance(self._items, set):
            self._items.add(item)
        else:
            raise ValueError('can only add item to list or set')

    def _pick(self):
        raise NotImplementedError

    def __iter__(self):
        return self

    def __next__(self):
        if self.empty():
            raise StopIteration
        return self._pick()


class FIFOSelector(Selector):
    def __init__(self):
        super().__init__([])
        self._init_index = 0

    def empty(self):
        return self._init_index >= len(self._items)

    def _pick(self):
        item = self._items[self._init_index]
        self._init_index += 1
        return item,


class RandomSelector(Selector):
    def __init__(self, random=None, n=1):
        super().__init__(set())
        import random as default_random
        self._random = random or default_random
        self.n = n

    def _pick(self):
        npick = self.n() if callable(self.n) else self.n
        picked = self._random.sample(self._items, min(npick, len(self._items)))
        for item in picked:
            self._items.discard(item)
        return tuple(picked)


class DelayedSelector(Selector):
    def __init__(self, lag):
        super().__init__(set())
        self.lag = lag
        self._time_counter = 0

    def empty(self):
        return len(self._items) == 0

    def add(self, item):
        lag_time = self.lag() if callable(self.lag) else self.lag
        item_with_lag_counter = (self._time_counter, lag_time, item)
        super(DelayedSelector, self).add(item_with_lag_counter)

    def _pick(self):
        items_to_pick = [(t0, dt, item) for (t0, dt, item) in self._items
                         if self._time_counter == t0 + dt]
        for picked in items_to_pick:
            self._items.discard(picked)
        self._time_counter += 1
        return tuple(item for (t0, dt, item) in items_to_pick)

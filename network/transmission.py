class GraphTransmission:
    def __init__(self, graph, from_node, test_transmit, selector):
        self.graph = graph
        self.originating_node = from_node
        self.test_transmit = test_transmit
        self._selector = selector
        self._nodes_broadcasted = set()
        self._step_index = 0
        self._tests = 0

        self._do_broadcast(self.originating_node)

    @property
    def broadcasts(self):
        return self._step_index

    @property
    def tests(self):
        return self._tests

    def __iter__(self):
        return self

    def _do_broadcast(self, node):
        for edge in self.graph.outbound_edges(node):
            self._selector.add(edge)
            self._nodes_broadcasted.add(node)
        self._step_index += 1

    def __next__(self):
        while not self._selector.empty():
            edges = []
            for edge in self._selector.remove():
                if edge.to_node not in self._nodes_broadcasted:
                    self._tests += 1
                    if self.test_transmit is None or self.test_transmit(self, edge):
                        self._do_broadcast(edge.to_node)
                        edges.append(edge)
            if not edges:
                continue
            return tuple(edges)
        raise StopIteration


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
    def __init__(self, random_=None):
        import random as default_random
        self._items = set()
        self._random = random_ or default_random

    def empty(self):
        return len(self._items) == 0

    def add(self, item):
        self._items.add(item)

    def remove(self):
        if self.empty():
            raise IndexError
        random_item = self._random.sample(self._items, 1)[0]
        self._items.remove(random_item)
        return random_item,


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

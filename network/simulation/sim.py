import random


# def run_simulation(graph, start, test_transmit=None,
#                    metadata=None, random_=None):
#     if random_ is None:
#         random_ = random.Random()
#     transmission = graph.transmit(start, test_transmit=test_transmit,
#                                   randomized=random_)
#     return Transmission(tuple(transmission), metadata)


# def random_graph(n_nodes, param_generator):
#     graph = Graph(range(n_nodes))
#
#     for node in graph.nodes:
#         edges_to_build = param_generator.follow_count(n_nodes)
#         pool = set(graph.nodes)
#         pool.remove(node)
#         for node_to_follow in random.sample(pool, edges_to_build):
#             graph.add_edge(edge=(node_to_follow, node),
#                            strength=param_generator.edge_strength())
#
#     return graph


class Simulation:
    def __init__(self, transmission, runner=None):
        self._transmission = transmission
        if not runner:
            self._runner = self._transmission
        else:
            self._runner = runner(transmission)

        self._saved_path = []
        self._history = []
        self._path_completed = False
        self._tracked_index = 0

    @property
    def history(self):
        return tuple(self._history)

    def _exec_transmission(self, steps):
        while steps is None or self._tracked_index < steps:
            try:
                next_path_segment = next(self._runner)
                self._history.append({
                    'steps': self._transmission.steps,
                    'broadcasts': self._transmission.broadcasts,
                    'tests': self._transmission.tests
                })
                self._saved_path.append(next_path_segment)
                self._tracked_index += 1
            except StopIteration:
                self._path_completed = True
                break

    def path(self, index=None):
        if index is None or (not self._path_completed and index >= len(self._saved_path)):
            self._exec_transmission(index)
        max_index = len(self._saved_path) if index is None else index
        return (seg for (i, seg) in enumerate(self._saved_path) if i < max_index)

    @property
    def originating_node(self):
        return self._transmission.originating_node

    @property
    def transmission(self):
        return self._transmission


def test(p):
    if callable(p):
        return random.random() < p()
    elif 0 <= p <= 1:
        return random.random() < p
    else:
        raise ValueError('p must be between 0 and 1')
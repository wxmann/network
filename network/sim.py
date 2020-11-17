import pickle
import random

from contextlib import contextmanager
from pathlib import Path

from network.graph import Graph


def run_simulation(graph, start, test_broadcast=None,
                   test_edge=None, metadata=None):
    transmission = graph.transmit(start, test_broadcast=test_broadcast,
                                  test_edge=test_edge)
    return Transmission(tuple(transmission), metadata)


def random_graph(n_nodes, param_generator):
    graph = Graph(range(n_nodes))

    for node in graph.nodes:
        edges_to_build = param_generator.follow_count(n_nodes)
        pool = set(graph.nodes)
        pool.remove(node)
        for node_to_follow in random.sample(pool, edges_to_build):
            graph.add_edge(edge=(node_to_follow, node),
                           strength=param_generator.edge_strength())

    return graph


class Transmission:
    def __init__(self, path, metadata=None):
        if len(path) < 1:
            raise ValueError('Path must be a list or tuple with entries')
        self.path = path
        self._metadata = metadata or {}

    @property
    def originating_node(self):
        return self.path[0].from_node

    @property
    def metadata(self):
        return dict(self._metadata)


def test(p):
    if callable(p):
        return random.random() < p()
    elif 0 <= p <= 1:
        return random.random() < p
    else:
        raise ValueError('p must be between 0 and 1')


def beta_rv(a, b):
    return _RV(random.betavariate, a=a, b=b)


def uniform_rv(a, b):
    return _RV(random.uniform, a=a, b=b)


class _RV:
    def __init__(self, func, **kwargs):
        self._func = func
        self._kwargs = kwargs
        self._factor = 1

    @property
    def params(self):
        return dict(self._kwargs)

    def __call__(self):
        return self._factor * self._func(*self._kwargs.values())

    def __mul__(self, other):
        self._factor = other

    def __rmul__(self, other):
        self._factor = other


def beta_params(mean, sd):
    u = mean
    s2 = sd ** 2
    alpha = (-u ** 3 + u ** 2 - u * s2) / s2
    beta = (u ** 3 - 2 * u ** 2 + u * s2 + u - s2) / s2
    if alpha < 0 or beta < 0:
        raise ValueError(f'cannot calculate alpha/beta for mean {mean} and sd {sd}')
    return alpha, beta


def get_fixed_state():
    pkl_dir = Path(__file__).resolve().parent
    with open(f'{pkl_dir}/sim_state.pkl', 'rb') as f:
        return pickle.load(f)


@contextmanager
def fix_random(rand=None, state=None):
    random_ = rand or random
    saved_state = random_.getstate()
    try:
        fixed_state = state or get_fixed_state()
        random_.setstate(fixed_state)
        yield
    finally:
        random_.setstate(saved_state)

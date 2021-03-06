import math
import random
from itertools import combinations, product

from network.draw import GraphDrawer
from network.graph import Graph
from network.randoms import fixed_random


def community_graph(n_communities, community_size, orphans,
                    n_strong_conns, n_weak_conns, *,
                    core_kw=None, strong_kw=None, weak_kw=None,
                    graph_fun=None):

    def _get_kw_func(kw):
        if not kw:
            return dict
        if not callable(kw):
            return lambda: kw
        return kw

    core_kw = _get_kw_func(core_kw)
    strong_kw = _get_kw_func(strong_kw)
    weak_kw = _get_kw_func(weak_kw)

    total_ppl = n_communities * community_size + orphans

    if not graph_fun:
        graph_fun = Graph.of_size

    g = graph_fun(total_ppl, directed=False)
    core_edges, node_community_map = communities(n_communities, community_size)

    for edge in core_edges:
        g.add_edge(edge, kind='core', **core_kw())

    for strong_edge in generate_edges(g, n_strong_conns):
        g.add_edge(strong_edge, kind='strong', **strong_kw())

    for weak_edge in generate_edges(g, n_weak_conns):
        g.add_edge(weak_edge, kind='weak', **weak_kw())

    return g, node_community_map


def generate_edges(graph, n):
    if graph.directed:
        raise ValueError('Graph must be undirected')

    n_nodes = len(graph.nodes)
    n_existing_edges = graph.num_edges
    n_combos_exist = int(n_nodes * (n_nodes - 1) / 2 - n_existing_edges)

    if n > n_combos_exist:
        raise ValueError('Too many outbound connections per node to generate edges')

    chosen_indices = set(random.sample(range(n_combos_exist), n))
    pool = (c for c in combinations(graph.nodes, 2) if not graph.contains_edge(c))

    for index, nodes in enumerate(pool):
        if index in chosen_indices:
            yield nodes


def communities(n_communities, community_size):
    node_community_map = NodeCommunityMap()
    node_index = 0

    for comm in range(n_communities):
        comm_nodes = range(node_index, node_index + community_size)
        for node in comm_nodes:
            node_community_map[node] = comm
        node_index += community_size

    def yielding_community_edges():
        for comm_nodes in node_community_map.invert().values():
            for edge in combinations(comm_nodes, 2):
                yield edge

    return yielding_community_edges(), node_community_map


class NodeCommunityMap(dict):
    def invert(self):
        community_to_nodes = {}
        for node in self:
            comm = self[node]
            if comm not in community_to_nodes:
                community_to_nodes[comm] = []
            community_to_nodes[comm].append(node)
        return community_to_nodes

    def is_same_community(self, n1, n2):
        if n1 not in self or n2 not in self:
            return False
        return self[n1] == self[n2]


def community_drawer(graph, node_community_map, **positions_kw):
    return GraphDrawer(
        graph,
        positions_func=CommunityNodePositions(node_community_map, **positions_kw)
    )


class CommunityNodePositions:
    def __init__(self, node_community_map, dim=1000, sparseness=2,
                 random_=None, rfactor=1.5):
        assert sparseness >= 1
        self.node_community_map = node_community_map
        self.n_comm = len(set(node_community_map.values()))
        self.side_len = int(math.ceil(math.sqrt(self.n_comm * sparseness)))
        self.n_squares = self.side_len ** 2

        self.sparseness = sparseness
        self.r = dim / (2 * self.side_len)
        self.dim = dim
        self._random = random_ or fixed_random()
        self.rfactor = rfactor

    def _ctr_coords_for(self, sq):
        x, y = sq
        return self.r * (2 * x + 1), self.r * (2 * y + 1)

    def _random_coord_within(self, sq):
        x0, y0 = self._ctr_coords_for(sq)
        # dr = random.gauss(mu=0, sigma=self.r * 1.5)
        dr = self.r * self.rfactor * self._random.betavariate(1.33, 1.33)
        dtheta = self._random.uniform(0, 2 * math.pi)
        dx = dr * math.cos(dtheta)
        dy = dr * math.sin(dtheta)
        return x0 + dx, y0 + dy

    def __call__(self, graph, start):
        self._random.seed(0)
        grid = list(product(range(self.side_len), range(self.side_len)))
        selected_sq = list(self._random.sample(grid, self.n_comm))
        not_selected = [sq for sq in grid if sq not in selected_sq]

        for node in graph.nodes:
            if node in self.node_community_map:
                comm = self.node_community_map[node]
                yield node, self._random_coord_within(selected_sq[comm])
            else:
                random_sq = self._random.choice(not_selected)
                yield node, self._random_coord_within(random_sq)
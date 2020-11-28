import math
from itertools import combinations, permutations

from network.draw import GraphDrawer
from network.graph import Graph
from network.randoms import fixed_random
from network.simulation import test


def community_graph(n_communities, community_size, orphans,
                    n_strong_conns, n_weak_conns, strengths):
    g = Graph()
    core_edges, node_community_map = communities(n_communities, community_size)

    for edge in core_edges:
        g.add_edge(edge, kind='core', strength=strengths['core'])

    for orphan_node in range(max(node_community_map) + 1, max(node_community_map) + orphans + 1):
        g.add_node(orphan_node)

    for strong_edge in generate_edges(g, n_strong_conns):
        g.add_edge(strong_edge, kind='strong', strength=strengths['strong'])

    for weak_edge in generate_edges(g, n_weak_conns):
        g.add_edge(weak_edge, kind='weak', strength=strengths['weak'])

    return g


def generate_edges(graph, n):
    n_nodes = len(graph.nodes)
    n_existing_edges = graph.num_edges / 2
    n_combos_need = n
    n_combos_exist = n_nodes * (n_nodes - 1) / 2 - n_existing_edges

    if n_combos_need > n_combos_exist:
        raise ValueError('Too many connections per capita to generate edges')
    p_take = n_combos_need / n_combos_exist

    for n1, n2 in combinations(graph.nodes, 2):
        if all([
            not graph.contains_edge((n1, n2)),
            not graph.contains_edge((n2, n1)),
            test(p_take)
        ]):
            yield n1, n2
            yield n2, n1
            n_combos_need -= 1

        n_combos_exist -= 1
        if n_combos_exist == 0 or n_combos_need == 0:
            raise StopIteration
        p_take = n_combos_need / n_combos_exist


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
    def __init__(self, node_community_map, dim=1000, sparseness=2, random_=None):
        assert sparseness >= 1
        self.node_community_map = node_community_map
        self.n_comm = len(set(node_community_map.values()))
        self.side_len = int(math.ceil(math.sqrt(self.n_comm * sparseness)))
        self.n_squares = self.side_len ** 2

        self.sparseness = sparseness
        self.r = dim / (2 * self.side_len)
        self.dim = dim
        self._random = random_ or fixed_random()

    def _ctr_coords_for(self, sq):
        x, y = sq
        return self.r * (2 * x + 1), self.r * (2 * y + 1)

    def _random_coord_within(self, sq):
        x0, y0 = self._ctr_coords_for(sq)
        # dr = random.gauss(mu=0, sigma=self.r * 1.5)
        dr = self.r * 1.5 * self._random.betavariate(1.33, 1.33)
        dtheta = self._random.uniform(0, 2 * math.pi)
        dx = dr * math.cos(dtheta)
        dy = dr * math.sin(dtheta)
        return x0 + dx, y0 + dy

    def __call__(self, graph, start):
        grid = list(permutations(range(self.side_len), 2))
        selected_sq = list(self._random.sample(grid, self.n_comm))
        not_selected = [sq for sq in grid if sq not in selected_sq]

        for node in graph.nodes:
            if node in self.node_community_map:
                comm = self.node_community_map[node]
                yield node, self._random_coord_within(selected_sq[comm])
            else:
                random_sq = self._random.choice(not_selected)
                yield node, self._random_coord_within(random_sq)
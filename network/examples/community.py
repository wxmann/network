import math
import random
from itertools import combinations, permutations

from network.graph import Graph
from network.simulation import test
from network.randoms import fixed_random


def community_graph(n_communities, community_size, orphans,
                    n_participants=3, n_fringes=10, core_p_connect=0.75,
                    core_kw=None, participant_kw=None, fringe_kw=None):

    core_kw, participant_kw, fringe_kw = _parse_kw(core_kw, participant_kw, fringe_kw)
    node_index = 0
    graph = Graph()
    node_community_map = {}

    # define useful closures
    def reverse(edge_):
        x1, x2 = edge_
        return x2, x1

    def add_bidirectional_edge(edge_, p_follow_back=0.4, **kwargs):
        start = random.choice([edge_, reverse(edge_)])
        if not graph.contains_edge(start):
            graph.add_edge(start, **kwargs)
        if test(p_follow_back) and not graph.contains_edge(reverse(start)):
            graph.add_edge(reverse(start), **kwargs)

    # generate core nodes/edges for each community
    for comm in range(n_communities):
        comm_nodes = range(node_index, node_index + community_size)
        for node in comm_nodes:
            node_community_map[node] = comm
        for edge in combinations(comm_nodes, 2):
            if test(core_p_connect):
                add_bidirectional_edge(edge, kind='core', **core_kw)
        node_index += community_size

    # add orphans
    for node in range(node_index, node_index + orphans):
        graph.add_node(node)

    # generate participants and fringe
    n_participants_tot = n_participants * n_communities
    n_fringes_tot = n_fringes * n_communities

    edge_combos = [edge for edge in combinations(graph.nodes, 2)
                   if all([
                        not graph.contains_edge(edge),
                        not graph.contains_edge(reverse(edge)),
                        edge[0] != edge[1],
                        node_community_map.get(edge[0], None) != node_community_map.get(edge[1], '')
                    ])]

    addtl_conns = random.sample(edge_combos, n_participants_tot + n_fringes_tot)

    for participant_edge in addtl_conns[0:n_participants_tot]:
        add_bidirectional_edge(participant_edge, kind='participant', **participant_kw)

    for fringe_edge in addtl_conns[n_participants_tot:]:
        add_bidirectional_edge(fringe_edge, kind='fringe', **fringe_kw)

    return graph, node_community_map


def _parse_kw(core_kw, participant_kw, fringe_kw):
    if not core_kw:
        core_kw = dict(
            p_follow_back=0.7,
            strength=0.7
        )
    if not participant_kw:
        participant_kw = dict(
            p_follow_back=0.5,
            strength=0.5
        )
    if not fringe_kw:
        fringe_kw = dict(
            p_follow_back=0.3,
            strength=0.3
        )
    return core_kw, participant_kw, fringe_kw


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
import unittest

from network.examples.community import NodeCommunityMap, communities, generate_edges
from network.graph import Graph
from network.randoms import fix_random


def test__should_generate_community_edges_and_map():
    edges, ncmap = communities(n_communities=3, community_size=3)
    assert ncmap == {
        0: 0, 1: 0, 2: 0,
        3: 1, 4: 1, 5: 1,
        6: 2, 7: 2, 8: 2
    }

    expected_edges = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1),
                      (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4),
                      (6, 7), (6, 8), (7, 6), (7, 8), (8, 6), (8, 7)]

    assert list(edges) == expected_edges


def test__should_generate_community_outbound_edges():
    edges, ncmap = communities(n_communities=3, community_size=3)
    g = Graph()
    for edge in edges:
        g.add_edge(edge)

    with fix_random():
        new_edges = generate_edges(g, 5)
        assert list(new_edges) == [
            (0, 5), (5, 0),
            (1, 5), (5, 1),
            (2, 4), (4, 2),
            (2, 6), (6, 2),
            (4, 8), (8, 4)
        ]


class TestNodeCommunityMap(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.ncmap = NodeCommunityMap()
        for node in range(3):
            self.ncmap[node] = 1
        for node in range(3, 6):
            self.ncmap[node] = 2
        self.ncmap[7] = 3

    def test__should_invert_node_community_map(self):
        self.assertDictEqual(self.ncmap.invert(), {
            1: [0, 1, 2],
            2: [3, 4, 5],
            3: [7]
        })

    def test__should_test_same_community(self):
        self.assertTrue(self.ncmap.is_same_community(3, 5))
        self.assertFalse(self.ncmap.is_same_community(3, 7))
        self.assertFalse(self.ncmap.is_same_community(3, 1111))






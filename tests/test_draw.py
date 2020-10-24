import unittest

from graph import Graph
from draw import GraphDrawer


class TestGraphDrawer(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = Graph()
        self.graph.add_edge((1, 2))
        self.graph.add_edge((1, 3))
        self.graph.add_edge((1, 4))
        self.graph.add_edge((2, 5))
        self.graph.add_edge((2, 6))
        self.graph.add_edge((3, 7))
        self.graph.add_edge((6, 7))
        self.graph.add_edge((4, 8))
        self.graph.add_edge((4, 9))
        self.graph.add_edge((4, 10))
        self.graph.add_edge((5, 11))
        self.graph.add_edge((6, 11))
        self.graph.add_edge((7, 11))
        self.graph.add_edge((7, 12))

        self.drawer = GraphDrawer(self.graph)

    def test__calculate_spans(self):
        spans = self.drawer._spans(1)
        self.assertDictEqual(spans, {
            0: {1: 1.0},
            1: {2: 0.3333333333333333, 3: 0.2222222222222222, 4: 0.4444444444444444},
            2: {5: 0.2, 6: 0.2, 7: 0.3, 8: 0.1, 9: 0.1, 10: 0.1},
            3: {11: 0.5, 12: 0.5}})


if __name__ == '__main__':
    unittest.main()

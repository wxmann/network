import unittest

from network.graph import Graph
from network.transmission import GraphTransmission, FIFOSelector, RandomSelector
from network.sim import fix_random


class TestGraphTransmission(unittest.TestCase):
    @staticmethod
    def _nodes_of(step):
        return step[0].from_node, step[0].to_node

    def setUp(self) -> None:
        super().setUp()
        self.graph = Graph()
        self.graph.add_edge((1, 2))
        self.graph.add_edge((2, 3))
        self.graph.add_edge((1, 3))
        self.graph.add_edge((1, 4))
        self.graph.add_edge((4, 3))
        self.graph.add_edge((3, 5))
        self.graph.add_edge((3, 2))
        self.graph.add_edge((2, 1))

    def test__should_transmit_fifo_through_graph_starting_from_top(self):
        path = [TestGraphTransmission._nodes_of(step)
                for step in GraphTransmission(self.graph, 1, FIFOSelector()) if step]
        self.assertListEqual(path, [
            (1, 2), (1, 3), (1, 4), (3, 5)
        ])

    def test__should_transmit_random_through_graph_starting_from_top(self):
        with fix_random():
            path = [TestGraphTransmission._nodes_of(step)
                    for step in GraphTransmission(self.graph, 1, RandomSelector()) if step]
            self.assertListEqual(path, [
                (1, 3), (3, 5), (1, 4), (1, 2)
            ])

    def test__should_transmit_fifo_through_graph_starting_from_middle(self):
        path = [TestGraphTransmission._nodes_of(step)
                for step in GraphTransmission(self.graph, 3, FIFOSelector()) if step]
        self.assertListEqual(path, [
            (3, 5), (3, 2), (2, 1), (1, 4)
        ])

    def test__should_transmit_through_graph_starting_from_middle_randomized(self):
        with fix_random():
            path = [TestGraphTransmission._nodes_of(step)
                    for step in GraphTransmission(self.graph, 3, RandomSelector()) if step]
            self.assertListEqual(path, [
                (3, 5), (3, 2), (2, 1), (1, 4)
            ])

    def test__get_number_of_broadcasts(self):
        transmission = GraphTransmission(self.graph, 3, FIFOSelector())
        tuple(transmission)
        self.assertEqual(transmission.broadcasts, 4)

    def test__get_number_of_tests(self):
        transmission = GraphTransmission(self.graph, 3, FIFOSelector())
        tuple(transmission)
        self.assertEqual(transmission.tests, 4)


if __name__ == '__main__':
    unittest.main()

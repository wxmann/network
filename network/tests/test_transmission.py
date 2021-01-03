import unittest

import pytest

from network.graph import Graph
from network.simulation import test as numtest
from network.transmission import GraphTransmission, FIFOSelector, RandomSelector, DelayedSelector
from network.randoms import fix_random


class TestGraphTransmission(unittest.TestCase):
    @staticmethod
    def _nodes_of(step):
        return list(
            edge.nodes for edge in step
        )

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

    def assertPathEqual(self, actual, expected, log_on_err=True):
        for expected_step, actual_step in zip(expected, actual):
            try:
                self.assertCountEqual(expected_step, actual_step)
            except AssertionError as e:
                if log_on_err:
                    print(f'Actual: {actual} | Expected: {expected}')
                raise e
        self.assertEqual(len(expected), len(actual))

    def test__should_transmit_fifo_through_graph_starting_from_top(self):
        path = [TestGraphTransmission._nodes_of(step)
                for step in GraphTransmission(self.graph, 1, FIFOSelector())]

        self.assertPathEqual(path, [[(1, 2)], [(1, 3)], [(1, 4)], [(3, 5)]])

    def test__should_transmit_fifo_through_graph_starting_from_middle(self):
        path = [TestGraphTransmission._nodes_of(step)
                for step in GraphTransmission(self.graph, 3, FIFOSelector())]

        self.assertListEqual(path, [[(3, 5)], [(3, 2)], [(2, 1)], [(1, 4)]])

    def test__should_transmit_lagged_starting_from_top(self):
        path = [TestGraphTransmission._nodes_of(step)
                for step in GraphTransmission(self.graph, 1, DelayedSelector(lag=2))]

        self.assertPathEqual(path, [[], [], [(1, 2), (1, 4), (1, 3)], [], [], [(3, 5)]])

    def test__should_transmit_fifo_with_persistent_broadcast(self):
        with fix_random():
            path = [TestGraphTransmission._nodes_of(step)
                    for step in GraphTransmission(
                    self.graph, 1, FIFOSelector(),
                    persist_broadcast=2, test_transmit=lambda trans, edge: numtest(0.75)
                )]

        self.assertPathEqual(
            path,
            [[(1, 3)], [(1, 4)], [(3, 2)], [], [], [(3, 5)], [], []]
        )

    def test__should_transmit_persistent_broadcast_even_after_emptied(self):
        one_edge_graph = Graph()
        one_edge_graph.add_edge((1, 2))
        path = [TestGraphTransmission._nodes_of(step)
                for step in GraphTransmission(
                one_edge_graph, 1, FIFOSelector(),
                persist_broadcast=2
            )]

        self.assertListEqual(path, [[(1, 2)], [], []])

    def test__get_number_of_broadcasts(self):
        transmission = GraphTransmission(self.graph, 3, FIFOSelector())
        tuple(transmission)
        self.assertEqual(transmission.broadcasts, 5)

    def test__get_number_of_tests(self):
        transmission = GraphTransmission(self.graph, 3, FIFOSelector())
        tuple(transmission)
        self.assertEqual(transmission.tests, 4)


def test__should_iterate_through_items_fifo_order():
    selector = FIFOSelector()
    for i in range(3):
        selector.add(i)
    picked_items = tuple(selector)
    assert picked_items == tuple((i,) for i in range(3))


def test__should_iterate_through_items_random_order():
    selector = RandomSelector(n=2)
    for i in range(3):
        selector.add(i)

    with fix_random():
        picked_items = tuple(selector)
        assert picked_items == ((1, 2), (0,))


def test__should_iterate_through_items_lagged():
    selector = DelayedSelector(lag=2)
    selector.add(0)
    selector.add(1)
    zeroth_item = next(selector)
    selector.add(2)
    first_item = next(selector)
    second_item = next(selector)
    third_item = next(selector)

    assert zeroth_item == ()
    assert first_item == ()
    assert second_item == (0, 1)
    assert third_item == (2,)

    with pytest.raises(StopIteration):
        next(selector)


if __name__ == '__main__':
    unittest.main()

import unittest
from collections import namedtuple

from network.graph import Graph


class TestGraph(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.graph = Graph()
        self.graph.add_edge((1, 2), strength=0.5)
        self.graph.add_edge((2, 1), strength=0.4)
        self.graph.add_edge((2, 3), strength=0.6)
        self.dummy_msg = namedtuple('msg', ['originating_node'])

    def test__should_retrieve_nodes(self):
        self.assertTupleEqual(tuple(self.graph.nodes), (1, 2, 3))

    def test__should_test_contains_node(self):
        self.assertTrue(self.graph.contains_node(2))
        self.assertFalse(self.graph.contains_node(5))

    def test__should_test_contains_leaf_node(self):
        self.assertTrue(self.graph.contains_node(3))

    def test__contains_edge_should_test_nodes_in_graph(self):
        self.assertTrue(self.graph.contains_edge((2, 1)))
        self.assertFalse(self.graph.contains_edge((2, 2)))

    def test__contains_edge_should_return_false_for_nonexistent_node(self):
        self.assertFalse(self.graph.contains_edge((4, 1)))

    def test__should_add_new_leaf_node_and_test_contains_it(self):
        self.graph.add_edge((3, 4), strength=0.1)
        self.assertTrue(self.graph.contains_node(4))
        self.assertTrue(self.graph.contains_edge((3, 4)))

    def test__should_return_edge_attributes(self):
        self.assertEqual(self.graph.get_edge_attrs((1, 2))['strength'], 0.5)

    def test__should_raise_error_if_get_edge_attrs_from_nonexistent_node(self):
        with self.assertRaises(ValueError):
            self.graph.get_edge_attrs((4, 2))

    def test__bfs_traverse_from_a_root_node(self):
        path = tuple(self.graph.traverse_edges(1))
        self.assertEqual(len(path), 3)

        first_edge = path[0]
        self.assertTupleEqual((first_edge.from_node, first_edge.to_node), (1, 2))

        second_edge = path[1]
        self.assertTupleEqual((second_edge.from_node, second_edge.to_node), (2, 1))

        third_edge = path[2]
        self.assertTupleEqual((third_edge.from_node, third_edge.to_node), (2, 3))

    def test__transmission_from_root_node(self):
        path = tuple(self.graph.transmit(1))
        self.assertEqual(len(path), 2)

        first_edge = path[0]
        self.assertTupleEqual((first_edge.from_node, first_edge.to_node), (1, 2))

        second_edge = path[1]
        self.assertTupleEqual((second_edge.from_node, second_edge.to_node), (2, 3))

    def test__bfs_traverse_from_a_leaf_node_no_children(self):
        path = tuple(self.graph.traverse_edges(3))
        self.assertEqual(len(path), 0)

    def test__bfs_traverse_from_nonexisting_node_should_fail(self):
        with self.assertRaises(ValueError):
            list(self.graph.traverse_edges(5))

    def test__should_return_immediate_children(self):
        self.graph.add_edge((1, 4), strength=0.6)
        children = next(self.graph.children(1))
        self.assertTupleEqual(tuple(children), (2, 4))

    def test__should_return_second_degree_children_not_excluding_dups(self):
        self.graph.add_edge((1, 4), strength=0.6)
        _, second_deg_children = tuple(self.graph.children(1, deg=2, exclude_dups=False))
        self.assertTupleEqual(tuple(second_deg_children), (1, 3))

    def test__should_return_second_degree_children_excluding_dups(self):
        self.graph.add_edge((1, 4), strength=0.6)
        _, second_deg_children = tuple(self.graph.children(1, deg=2, exclude_dups=True))
        self.assertTupleEqual(tuple(second_deg_children), (3,))

    def test__should_return_empty_children_from_leaf_node(self):
        children = next(self.graph.children(3))
        self.assertTupleEqual(tuple(children), ())

    def test__should_return_children_from_node_indefinitely_if_deg_is_None(self):
        multichildren = self.graph.children(3, deg=None)
        for _ in range(4):
            children = next(multichildren)
            self.assertTupleEqual(tuple(children), ())

    def test__should_create_a_graph_with_empty_nodes(self):
        graph = Graph(range(10))
        self.assertTupleEqual(tuple(graph.nodes), tuple(range(10)))


class TestGraphTransmit(unittest.TestCase):

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

    def test__should_transmit_through_graph_starting_from_top(self):
        path = [(edge.from_node, edge.to_node) for edge in self.graph.transmit(1)]
        self.assertListEqual(path, [
            (1, 2), (1, 3), (1, 4), (3, 5)
        ])

    def test__should_transmit_through_graph_starting_from_top_with_steps(self):
        path = [(step, edge.from_node, edge.to_node)
                for step, edge in self.graph.transmit(1, steps=True)]
        self.assertListEqual(path, [
            (0, 1, 2), (0, 1, 3), (0, 1, 4), (2, 3, 5)
        ])

# TODO: fix state of random
    # def test__should_transmit_through_graph_starting_from_top_randomized(self):
    #     import random
    #     random.seed(0)
    #     path = [(step, edge.from_node, edge.to_node)
    #             for step, edge in self.graph.transmit(1, steps=True, randomized=True)]
    #     self.assertEqual(len(path), 4)
    #     print(path)
    #     for piece in [(1, 2), (1, 3), (1, 4), (3, 5)]:
    #         self.assertTrue(piece in path)

    def tests__should_transmit_through_graph_starting_from_middle(self):
        path = [(edge.from_node, edge.to_node) for edge in self.graph.transmit(3)]
        self.assertListEqual(path, [
            (3, 5), (3 ,2), (2, 1), (1, 4)
        ])

    def test__should_transmit_through_graph_starting_from_middle_with_steps(self):
        path = [(step, edge.from_node, edge.to_node)
                for step, edge in self.graph.transmit(3, steps=True)]
        self.assertListEqual(path, [
            (0, 3, 5), (0, 3 ,2), (2, 2, 1), (3, 1, 4)
        ])


if __name__ == '__main__':
    unittest.main()

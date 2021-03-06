import unittest

from network.graph import Graph


class TestGraph(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.graph = Graph()
        self.graph.add_edge((1, 2), strength=0.5)
        self.graph.add_edge((2, 1), strength=0.4)
        self.graph.add_edge((2, 3), strength=0.6)

        self.undirected_graph = Graph(directed=False)
        self.undirected_graph.add_edge((1, 2), strength=0.5)
        self.undirected_graph.add_edge((2, 3), strength=0.6)

    def test__should_retrieve_nodes(self):
        self.assertTupleEqual(tuple(self.graph.nodes), (1, 2, 3))

    def test__should_get_num_edges_directed(self):
        self.graph.add_edge((2, 4), strength=0.6)
        self.graph.add_edge((2, 5), strength=0.6)
        self.graph.add_edge((4, 6), strength=0.6)
        self.graph.add_edge((4, 7), strength=0.6)

        self.assertEqual(self.graph.num_edges, 7)

    def test__should_get_num_edges_undirected(self):
        self.undirected_graph.add_edge((2, 4), strength=0.6)
        self.undirected_graph.add_edge((2, 5), strength=0.6)
        self.undirected_graph.add_edge((4, 6), strength=0.6)
        self.undirected_graph.add_edge((4, 7), strength=0.6)

        self.assertEqual(self.undirected_graph.num_edges, 6)

    def test__should_test_contains_node(self):
        self.assertTrue(self.graph.contains_node(2))
        self.assertFalse(self.graph.contains_node(5))

    def test__should_test_contains_leaf_node(self):
        self.assertTrue(self.graph.contains_node(3))

    def test__should_remove_edge(self):
        removed_edge = self.graph.remove_edge((2, 1))
        self.assertListEqual(
            [(edge.from_node, edge.to_node) for edge in self.graph.iter_edges()],
            [(1, 2), (2, 3)]
        )
        nonexistent_edge = self.graph.remove_edge((1, 9))
        self.assertIsInstance(removed_edge, dict)
        self.assertIsNone(nonexistent_edge)
        self.assertEqual(self.graph.num_edges, 2)

    def test__should_remove_edge_undirected(self):
        removed_edges = self.undirected_graph.remove_edge((2, 1))
        self.assertEqual(len(removed_edges), 2)
        self.assertListEqual(
            [(edge.from_node, edge.to_node) for edge in self.undirected_graph.iter_edges()],
            [(2, 3)]
        )
        self.assertEqual(self.undirected_graph.num_edges, 1)

    def test__should_iter_edges_undirected(self):
        self.undirected_graph.add_edge((2, 4), strength=0.6)
        self.undirected_graph.add_edge((5, 2), strength=0.6)
        self.undirected_graph.add_edge((6, 4), strength=0.6)
        self.undirected_graph.add_edge((4, 7), strength=0.6)

        self.assertListEqual(
            [(edge.from_node, edge.to_node) for edge in self.undirected_graph.iter_edges()],
            [(1, 2), (2, 3), (2, 4), (2, 5), (4, 6), (4, 7)]
        )

    def test__should_update_edge(self):
        self.graph.update_edge((2, 1), strength=0)
        self.assertDictEqual(self.graph.get_edge_attrs((2, 1)), dict(strength=0))

    def test__should_update_edge_undirected(self):
        self.undirected_graph.update_edge((2, 1), strength=0)
        self.assertDictEqual(self.undirected_graph.get_edge_attrs((2, 1)), dict(strength=0))
        self.assertDictEqual(self.undirected_graph.get_edge_attrs((1, 2)), dict(strength=0))

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

    def test__should_not_add_undirected_edge_twice(self):
        self.undirected_graph.add_edge((1, 10))
        with self.assertRaises(ValueError):
            self.undirected_graph.add_edge((10, 1))

    def test__should_duplicate_graph(self):
        duplicated = Graph.duplicate(self.graph)
        self.assertEqual(len(duplicated.nodes), 3)
        self.assertTrue(duplicated.directed)
        self.assertListEqual(
            [(edge.from_node, edge.to_node) for edge in duplicated.iter_edges()],
            [(1, 2), (2, 1), (2, 3)]
        )
        self.assertFalse(duplicated is self.graph)

        duplicated_undirected = Graph.duplicate(self.undirected_graph)
        self.assertEqual(len(duplicated_undirected.nodes), 3)
        self.assertFalse(duplicated_undirected.directed)
        self.assertListEqual(
            [(edge.from_node, edge.to_node) for edge in duplicated_undirected.iter_edges()],
            [(1, 2), (2, 3)]
        )


if __name__ == '__main__':
    unittest.main()

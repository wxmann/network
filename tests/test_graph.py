import unittest

from graph import Graph


class TestGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = Graph()
        self.graph.add_edge((1, 2), strength=0.5)
        self.graph.add_edge((2, 1), strength=0.4)
        self.graph.add_edge((2, 3), strength=0.6)

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
        self.assertTupleEqual(tuple(self.graph.bfs_traversal(1)), (1, 2, 3))

    def test__bfs_traverse_from_a_leaf_node_no_children(self):
        self.assertTupleEqual(tuple(self.graph.bfs_traversal(3)), (3,))

    def test__bfs_traverse_from_nonexisting_node_should_fail(self):
        with self.assertRaises(ValueError):
            list(self.graph.bfs_traversal(5))

    def test__bfs_traverse_with_take_predicate(self):
        traversed = tuple(self.graph.bfs_traversal(2, take=lambda edge: edge.strength > 0.5))
        self.assertTupleEqual(traversed, (2, 3))

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


if __name__ == '__main__':
    unittest.main()

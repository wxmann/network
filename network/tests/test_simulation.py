import unittest

from network.graph import Graph
from network.randoms import fix_random
from network.simulation import Simulation
from network.transmission import GraphTransmission, FIFOSelector


class TestSimulation(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.graph = Graph()
        self.graph.add_edge((1, 2))
        self.graph.add_edge((1, 3))
        self.graph.add_edge((1, 4))
        self.graph.add_edge((1, 5))
        self.transmission = GraphTransmission(self.graph, 1, selector=FIFOSelector())

    @staticmethod
    def _nodes_of(step):
        return list(
            edge.nodes for edge in step
        )

    def test_run_simulation_default_runner(self):
        sim = Simulation(self.transmission)
        with fix_random():
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(1)],
                [[(1, 2)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(3)],
                [[(1, 2)], [(1, 3)], [(1, 4)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(100)],
                [[(1, 2)], [(1, 3)], [(1, 4)], [(1, 5)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path()],
                [[(1, 2)], [(1, 3)], [(1, 4)], [(1, 5)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(2)],
                [[(1, 2)], [(1, 3)]]
            )

    def test_run_simulation_runner_adds_nodes(self):

        def runner(transmission):
            graph = transmission.graph
            addend = 2
            while True:
                try:
                    yield next(transmission)
                except StopIteration:
                    return
                if addend + 4 <= 10:
                    graph.add_edge((4, addend + 4))
                    addend += 1

        sim = Simulation(self.transmission, runner)
        with fix_random():
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(1)],
                [[(1, 2)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(3)],
                [[(1, 2)], [(1, 3)], [(1, 4)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path()],
                [[(1, 2)], [(1, 3)], [(1, 4)], [(1, 5)], [(4, 6)], [(4, 7)]]
            )
            self.assertListEqual(
                [TestSimulation._nodes_of(step) for step in sim.path(2)],
                [[(1, 2)], [(1, 3)]]
            )


if __name__ == '__main__':
    unittest.main()

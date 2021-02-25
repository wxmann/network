from network.simulation import test, Simulation
from network.transmission import GraphTransmission, DelayedSelector


def virus_simulation(graph, patient0, incubation_period, contagious_for,
                     runner, test_transmit=None):
    if not test_transmit:
        test_transmit = lambda trans, edge: test(edge.attr('strength'))

    transmission = GraphTransmission(
        graph, patient0,
        selector=DelayedSelector(incubation_period),
        test_transmit=test_transmit,
        persist_broadcast=contagious_for
    )
    return Simulation(transmission, runner=runner)


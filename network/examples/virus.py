from network.examples.community import generate_edges
from network.simulation import test, Simulation
from network.transmission import GraphTransmission, DelayedSelector


def virus_simulation(graph, patient0, incubation_period, contagious_for, strengths):
    transmission = GraphTransmission(
        graph, patient0, selector=DelayedSelector(incubation_period),
        test_transmit=lambda trans, edge: test(edge.strength),
        persist_broadcast=contagious_for
    )
    return Simulation(transmission, runner=virus_runner(graph, strengths))


def virus_runner(graph, strengths):
    if not all([
        'strong' in strengths,
        'weak' in strengths
    ]):
        raise ValueError('Strengths must be a dict with `strong`, and `weak` keys')

    def reset_weak_edges():
        num_weak_edges = 0
        for prev_weak_edge in (edge for edge in graph.iter_edges() if edge.kind == 'weak'):
            graph.remove_edge(prev_weak_edge.nodes)
            num_weak_edges += 1

        for new_weak_edge in generate_edges(graph, num_weak_edges):
            graph.add_edge(new_weak_edge, kind='weak', strength=strengths['weak'])

    def update_strong_edges():
        for strong_edge in (edge for edge in graph.iter_edges() if edge.kind == 'strong'):
            # 50-50 chance of seeing a strong edge
            if test(0.5):
                strong_edge.update(strength=0)
            else:
                strong_edge.update(strength=strengths['strong'])

    def runner(transmission):
        while True:
            update_strong_edges()
            yield next(transmission)
            reset_weak_edges()

    return runner
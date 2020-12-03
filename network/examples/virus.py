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
        edges_to_remove = [edge for edge in graph.iter_edges() if edge.kind == 'weak']
        for prev_weak_edge in edges_to_remove:
            graph.remove_edge(prev_weak_edge.nodes)

        n_new_weak_edges = int(len(edges_to_remove) / 2)
        for new_weak_edge in generate_edges(graph, n_new_weak_edges):
            graph.add_edge(new_weak_edge, kind='weak', strength=strengths['weak'])

    def update_strong_edges():
        for strong_edge in (edge for edge in graph.iter_edges() if edge.kind == 'strong'):
            # 50-50 chance of seeing a strong edge
            if test(0.5):
                graph.update_edge(strong_edge.nodes, strength=0)
            else:
                graph.update_edge(strong_edge.nodes, strength=strengths['strong'])

    def runner(transmission):
        while True:
            update_strong_edges()
            try:
                yield next(transmission)
            except StopIteration:
                return
            reset_weak_edges()

    return runner

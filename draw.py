class GraphDrawer:
    def __init__(self, graph):
        self.graph = graph

    def _spans(self, start):
        result = {0: {start: 1.0}}
        child_iter = self.graph.children(start, deg=None)
        for lev, nodes in enumerate(child_iter, start=1):
            if not nodes:
                break
            node_set = set(nodes)
            sum_dict = {node: 1 + len([child for child
                                       in next(self.graph.children(node, deg=1))
                                       if child not in node_set])
                        for node in nodes}
            total_sum = sum(sum_dict.values())
            result[lev] = {node: sum_dict[node] / total_sum for node in nodes}
        return result
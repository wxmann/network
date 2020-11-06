import math
import random

import matplotlib.pyplot as plt


def _spans(graph, start):
    yield {start: 1.0}
    child_iter = graph.children(start, deg=None)
    for nodes in child_iter:
        if not nodes:
            break
        node_set = set(nodes)
        sum_dict = {node: 1 + len([child for child
                                   in next(graph.children(node, deg=1))
                                   if child not in node_set])
                    for node in nodes}
        total_sum = sum(sum_dict.values())
        yield {node: sum_dict[node] / total_sum for node in nodes}


class _NodePoint:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color


class _EdgeLine:
    def __init__(self, x1, y1, dx, dy, color, alpha):
        self.x1 = x1
        self.y1 = y1
        self.dx = dx
        self.dy = dy
        self.color = color
        self.alpha = alpha


class _GraphDrawerMetadata:
    def __init__(self, graph, start):
        self._graph = graph
        self._node_map = dict(self._iter_nodepoints(start))
        self._edge_map = dict(self._iter_edgelines(start))

    def _positions(self, start):
        spans = list(_spans(self._graph, start))
        min_R = 0
        dR = 100
        for lev_spans in spans:
            dR_adjustment = math.sqrt(len(lev_spans) * len(spans) / len(self._graph.nodes))
            max_R = min_R + dR * dR_adjustment

            min_theta = 0
            for node, node_span in lev_spans.items():
                max_theta = min_theta + node_span * 2 * math.pi

                r_pos = random.uniform(min_R, max_R) if min_R != 0 else 0
                theta_pos = (min_theta + max_theta) / 2
                x = r_pos * math.cos(theta_pos)
                y = r_pos * math.sin(theta_pos)
                yield node, (x, y)

                min_theta = max_theta

            min_R = max_R

    def _iter_nodepoints(self, start):
        for node, (x, y) in self._positions(start):
            yield node, _NodePoint(x, y, color='blue')

    def _iter_edgelines(self, start):
        for edge in self._graph.traverse_edges(start):
            start_pt = self._node_map[edge.from_node]
            end_pt = self._node_map[edge.to_node]
            x1, y1 = start_pt.x, start_pt.y
            x2, y2 = end_pt.x, end_pt.y

            yield edge, _EdgeLine(x1, y1, dx=(x2 - x1), dy=(y2 - y1),
                                  color='black', alpha=0.15)

    @property
    def xs(self):
        return tuple(pt.x for pt in self._node_map.values())

    @property
    def ys(self):
        return tuple(pt.y for pt in self._node_map.values())

    @property
    def cs(self):
        return tuple(pt.color for pt in self._node_map.values())

    @property
    def arrow_coords(self):
        return self._edge_map.values()


class GraphDrawer:
    def __init__(self, graph):
        self.graph = graph

    def draw(self, start, s=None, arrows=True, arrow_kw=None):
        if s is None:
            s = 50
        if arrow_kw is None:
            arrow_kw = dict(
                head_width=10,
                head_length=15,
                overhang=0.6
            )

        plot_meta = _GraphDrawerMetadata(self.graph, start)

        scatter_pc = plt.scatter(plot_meta.xs, plot_meta.ys, s=s, c=plot_meta.cs)
        arrow_coll = []

        if arrows:
            for edge_coords in plot_meta.arrow_coords:
                arrow = plt.arrow(edge_coords.x1, edge_coords.y1,
                                  edge_coords.dx, edge_coords.dy,
                                  length_includes_head=True,
                                  color=edge_coords.color, alpha=edge_coords.alpha,
                                  **arrow_kw)
                arrow_coll.append(arrow)

        return scatter_pc, arrow_coll

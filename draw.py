import math
import random

import matplotlib.pyplot as plt


class GraphDrawer:
    def __init__(self, graph):
        self.graph = graph

    def _spans(self, start):
        result = [{start: 1.0}]
        child_iter = self.graph.children(start, deg=None)
        for nodes in child_iter:
            if not nodes:
                break
            node_set = set(nodes)
            sum_dict = {node: 1 + len([child for child
                                       in next(self.graph.children(node, deg=1))
                                       if child not in node_set])
                        for node in nodes}
            total_sum = sum(sum_dict.values())
            result.append({node: sum_dict[node] / total_sum for node in nodes})
        return result

    def _positions(self, spans, box_dim):
        width, height = box_dim
        dR = min(width, height) / len(spans)
        min_R = 0
        for lev, lev_spans in enumerate(spans):
            dR_adjustment = len(lev_spans) * len(spans) / len(self.graph.nodes)
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

    def draw(self, start, box_dim=None, s=None, arrow_kw=None):
        if box_dim is None:
            box_dim = (500, 500)
        if s is None:
            s = 200
        if arrow_kw is None:
            arrow_kw = dict(
                head_width=10,
                head_length=15,
                overhang=0.6
            )

        spans = self._spans(start)
        coords = dict(self._positions(spans, box_dim))
        xs = [coord[0] for coord in coords.values()]
        ys = [coord[1] for coord in coords.values()]

        plt.scatter(xs, ys, s=s)

        for edge in self.graph.bfs_traversal(start, output='edges'):
            x1, y1 = coords[edge.from_node]
            x2, y2 = coords[edge.to_node]
            plt.arrow(x1, y1, (x2 - x1), (y2 - y1), length_includes_head=True, **arrow_kw)

import math
import random

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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
    def __init__(self, x1, y1, dx, dy, color, alpha=None):
        self.x1 = x1
        self.y1 = y1
        self.dx = dx
        self.dy = dy
        self.color = color
        self.alpha = alpha


class _MplGraphPlotter:
    def __init__(self, graph, start):
        self._graph = graph
        self._node_map = dict(self._iter_nodepoints(start))
        self._edge_map = dict(self._iter_edgelines(start))
        self._scat = None
        self._arrows = None

    @property
    def scat(self):
        return self._scat

    @property
    def arrows_list(self):
        return list(self._arrows.values())

    @property
    def artists(self):
        return [self.scat] + self.arrows_list

    def _positions(self, start):
        spans = list(_spans(self._graph, start))
        min_R = 0
        dR = 100
        for lev_spans in spans:
            dR_adjustment = math.sqrt(
                len(lev_spans) * len(spans) / len(self._graph.nodes)
            )
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

            yield edge, _EdgeLine(
                x1, y1,
                dx=(x2 - x1), dy=(y2 - y1),
                color='black'
            )

    def refresh(self, nodes=True, edges=True):
        if nodes and self._scat is not None:
            self._scat.set_facecolors(
                tuple(pt.color for pt in self._node_map.values())
            )
        if edges and self._arrows is not None:
            for edge, patch in self._arrows.items():
                edgeline = self._edge_map.get(edge, None)
                if edgeline is not None:
                    patch.set_color(edgeline.color)
                    patch.set_alpha(edgeline.alpha)

    def plot_nodes(self, **additional_kw):
        self._scat = plt.scatter(
            tuple(pt.x for pt in self._node_map.values()),
            tuple(pt.y for pt in self._node_map.values()),
            c=tuple(pt.color for pt in self._node_map.values()),
            **additional_kw
        )

    def plot_edges(self, alpha=0.15, **additional_kw):
        self._arrows = {}
        for edge, edgeline in self._edge_map.items():
            edgeline.alpha = alpha
            arrow = plt.arrow(edgeline.x1, edgeline.y1,
                              edgeline.dx, edgeline.dy,
                              length_includes_head=True,
                              color=edgeline.color, alpha=edgeline.alpha,
                              **additional_kw)
            self._arrows[edge] = arrow

    def set_node(self, node, new_color):
        self._node_map[node].color = new_color

    def set_edge(self, edge, new_color, new_alpha=None):
        edgeline = self._edge_map[edge]
        edgeline.color = new_color
        if new_alpha is not None:
            edgeline.alpha = new_alpha


class GraphDrawer:
    def __init__(self, graph):
        self.graph = graph

    def draw(self, start, s=None, arrows=True, alpha=0.15, arrow_kw=None):
        if s is None:
            s = 50
        if arrow_kw is None:
            arrow_kw = dict(
                head_width=10,
                head_length=15,
                overhang=0.6
            )

        plotter = _MplGraphPlotter(self.graph, start)
        plotter.plot_nodes(s=s)
        plotter.plot_edges(alpha=alpha, **arrow_kw) if arrows else []
        return plotter


class GraphAnimator:
    def __init__(self, graph, start):
        self.graph = graph
        self.start = start
        self.drawer = GraphDrawer(self.graph)
        self.plotter = None

    def animate(self, fig, transmission,
                every=3, max_frames=None,
                marked_color='red', marked_alpha=0.2,
                **kwargs):

        def update(edges_traversed):
            if not edges_traversed:
                self.plotter.set_node(transmission.originating_node, marked_color)
            else:
                for edge in edges_traversed:
                    self.plotter.set_edge(edge, marked_color, marked_alpha)
                    self.plotter.set_node(edge.from_node, marked_color)
                    self.plotter.set_node(edge.to_node, marked_color)
            self.plotter.refresh()

        def gen_func():
            yield None
            chunked = chunks(transmission.path, every)
            for i, chunk in enumerate(chunked):
                if max_frames and i >= max_frames:
                    return
                yield chunk

        def init():
            self.plotter = self.drawer.draw(self.start, **kwargs)

        return FuncAnimation(fig, update, frames=gen_func, init_func=init)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

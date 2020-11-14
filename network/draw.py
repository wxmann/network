import math
import random

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
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


def radial_positions(graph, start):
    spans = list(_spans(graph, start))
    min_R = 0
    dR = 100
    for lev_spans in spans:
        dR_adjustment = math.sqrt(
            len(lev_spans) * len(spans) / len(graph.nodes)
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


class _NodePoint:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color


class _EdgeLine:
    def __init__(self, x1, y1, dx, dy, color):
        self.x1 = x1
        self.y1 = y1
        self.dx = dx
        self.dy = dy
        self.color = color


class GraphPlotter:
    def __init__(self, graph, start, position_func=None):
        self._graph = graph
        self._start = start
        self._positions = position_func or radial_positions
        self._node_map = dict(self._iter_nodepoints())
        self._edge_map = dict(self._iter_edgelines())
        self._scat = None
        self._arrows = None
        self._changed_artists = []

    @property
    def scat(self):
        return self._scat

    @property
    def arrows_list(self):
        return list(self._arrows.values())

    @property
    def artists(self):
        if not self._changed_artists:
            return [self.scat] + self.arrows_list
        return self._changed_artists

    def _iter_nodepoints(self):
        for node, (x, y) in self._positions(self._graph, self._start):
            yield node, _NodePoint(x, y, color='blue')

    def _iter_edgelines(self):
        for edge in self._graph.iter_edges():
            start_pt = self._node_map[edge.from_node]
            end_pt = self._node_map[edge.to_node]
            x1, y1 = start_pt.x, start_pt.y
            x2, y2 = end_pt.x, end_pt.y

            yield edge, _EdgeLine(
                x1, y1,
                dx=(x2 - x1), dy=(y2 - y1),
                color='black'
            )

    @staticmethod
    def _patch_aligned(patch, edgeline):
        edgecolor = patch.get_edgecolor()
        facecolor = patch.get_facecolor()
        return all([
            to_rgba(edgecolor) == to_rgba(edgeline.color),
            to_rgba(facecolor) == to_rgba(edgeline.color)
        ])

    def refresh(self, nodes=True, edges=True, for_blit=True):
        if for_blit:
            self._changed_artists = []

        if nodes and self._scat is not None:
            self._scat.set_facecolors(
                tuple(pt.color for pt in self._node_map.values())
            )
            if for_blit:
                self._changed_artists.append(self._scat)

        if edges and self._arrows is not None:
            for edge, patch in self._arrows.items():
                edgeline = self._edge_map[edge]
                if not for_blit:
                    patch.set_color(edgeline.color)
                elif not GraphPlotter._patch_aligned(patch, edgeline):
                    patch.set_color(edgeline.color)
                    self._changed_artists.append(patch)

    def plot_nodes(self, **additional_kw):
        self._scat = plt.scatter(
            tuple(pt.x for pt in self._node_map.values()),
            tuple(pt.y for pt in self._node_map.values()),
            c=tuple(pt.color for pt in self._node_map.values()),
            **additional_kw
        )

    def plot_edges(self, **additional_kw):
        self._arrows = {}
        for edge, edgeline in self._edge_map.items():
            arrow = plt.arrow(edgeline.x1, edgeline.y1,
                              edgeline.dx, edgeline.dy,
                              length_includes_head=True,
                              color=edgeline.color,
                              **additional_kw)
            self._arrows[edge] = arrow

    def set_node(self, node, new_color):
        self._node_map[node].color = new_color

    def set_edge(self, edge, new_color):
        edgeline = self._edge_map[edge]
        edgeline.color = new_color


class GraphDrawer:
    def __init__(self, graph, positions_func=None):
        self.graph = graph
        self._positions = positions_func

    def _generate_plotter(self, start):
        return GraphPlotter(self.graph, start, self._positions)

    def draw(self, start, s=40, linewidth=1, arrows=True, arrow_kw=None,
             plotter_inst=None):
        if arrow_kw is None:
            arrow_kw = dict(
                head_width=10,
                head_length=15,
                overhang=0.75
            )
        plotter = plotter_inst or self._generate_plotter(start)
        plotter.plot_nodes(s=s)
        plotter.plot_edges(linewidth=linewidth, **arrow_kw) if arrows else []
        return plotter

    @property
    def animate(self):
        return GraphAnimator(self)


class GraphAnimator:
    def __init__(self, drawer):
        self.drawer = drawer
        self._plotter = None

    def frame(self, n, transmission, marked_color='red', **draw_kw):
        plotter = self.drawer._generate_plotter(transmission.originating_node)

        for i, edge in enumerate(transmission.path):
            if i >= n:
                break
            plotter.set_edge(edge, marked_color)
            plotter.set_node(edge.from_node, marked_color)
            plotter.set_node(edge.to_node, marked_color)
        plotter.refresh(True)

        return self.drawer.draw(transmission.originating_node,
                                plotter_inst=plotter, **draw_kw)

    def __call__(self, transmission, fig=None,
                 every=3, max_frames=None,
                 marked_color='red', blit=True,
                 **draw_kw):

        def update(edges_traversed):
            if not edges_traversed:
                self._plotter.set_node(transmission.originating_node, marked_color)
            else:
                for edge in edges_traversed:
                    self._plotter.set_edge(edge, marked_color)
                    self._plotter.set_node(edge.from_node, marked_color)
                    self._plotter.set_node(edge.to_node, marked_color)
            self._plotter.refresh(for_blit=blit)
            return self._plotter.artists

        def gen_func():
            yield None
            chunked = chunks(transmission.path, every)
            for i, chunk in enumerate(chunked):
                if max_frames and i >= max_frames:
                    return
                yield chunk

        def init():
            self._plotter = self.drawer.draw(transmission.originating_node, **draw_kw)
            return self._plotter.artists

        return FuncAnimation(fig or plt.gcf(), update,
                             frames=gen_func, init_func=init, blit=blit)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

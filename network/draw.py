import itertools
import math

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.animation import FuncAnimation

from network.randoms import fixed_random


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
    random = fixed_random()
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
    def __init__(self, x1, y1, dx, dy, color, linewidth=None):
        self.x1 = x1
        self.y1 = y1
        self.dx = dx
        self.dy = dy
        self.color = color
        self.linewidth = linewidth or 1.0


class GraphPlotter:
    def __init__(self, graph, start, position_func=None):
        self._graph = graph
        self._start = start
        self._positions = position_func or radial_positions
        self._node_map = dict(self._iter_nodepoints())
        self._edge_map = dict(self._iter_edgelines())
        self._scat = None
        self._quiver = None

    @property
    def artists(self):
        return self._scat, self._quiver

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

    def refresh(self, nodes=True, edges=True):
        if nodes and self._scat is not None:
            self._scat.set_facecolors(
                tuple(pt.color for pt in self._node_map.values())
            )

        if edges and self._quiver is not None:
            self._quiver.set_facecolors(
                tuple(edge.color for edge in self._edge_map.values())
            )
            self._quiver.set_color(
                tuple(to_rgba(edge.color) for edge in self._edge_map.values())
            )

    def plot_nodes(self, **additional_kw):
        self._scat = plt.scatter(
            tuple(pt.x for pt in self._node_map.values()),
            tuple(pt.y for pt in self._node_map.values()),
            c=tuple(pt.color for pt in self._node_map.values()),
            **additional_kw
        )

    def plot_edges(self, linewidth=None):
        x, y, u, v, colors, lws = tuple([] for _ in range(6))

        for edge, edgeline in self._edge_map.items():
            GraphPlotter._set_linewidth(edge, edgeline, linewidth)
            x.append(edgeline.x1)
            y.append(edgeline.y1)
            u.append(edgeline.dx)
            v.append(edgeline.dy)
            colors.append(edgeline.color)
            lws.append(edgeline.linewidth)

        self._quiver = plt.quiver(x, y, u, v, angles='xy', scale_units='xy', scale=1,
                                  **GraphPlotter._generate_quiver_kw(lws, colors))

    @staticmethod
    def _generate_quiver_kw(lws, colors):
        # HACK: reducing width and increasing lw param allows lw < 1.0 to be plotted
        factor = 200
        width = 0.005 / factor
        if not lws:
            lws = None
            min_lw = 1.0
        else:
            min_lw = min(lws)

        return dict(
            lw=lws * factor,
            edgecolors=colors,
            color=colors,
            width=width,
            headwidth=3 * factor * min_lw,
            headlength=5 * factor * min_lw,
            headaxislength=3.5 * factor * min_lw
        )

    @staticmethod
    def _set_linewidth(edge, edgeline, linewidth):
        if linewidth is not None:
            if edge.strength is not None and isinstance(linewidth, tuple):
                minwidth, maxwidth = linewidth
                edgeline.linewidth = edge.strength * (maxwidth - minwidth) + minwidth
            else:
                edgeline.linewidth = linewidth

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

    def draw(self, start, s=40, linewidth=1, arrows=True, plotter_inst=None):
        plotter = plotter_inst or self._generate_plotter(start)
        plotter.plot_nodes(s=s)
        plotter.plot_edges(linewidth=linewidth) if arrows else []
        return plotter

    @property
    def animate(self):
        return GraphAnimator(self)


class GraphAnimator:
    def __init__(self, drawer):
        self.drawer = drawer
        self._plotter = None

    def frame(self, n, simulation, marked_color='red', arrows=True, **draw_kw):
        plotter = self.drawer._generate_plotter(simulation.originating_node)

        for segment in simulation.path(n):
            for edge in segment:
                if arrows:
                    plotter.set_edge(edge, marked_color)
                plotter.set_node(edge.from_node, marked_color)
                plotter.set_node(edge.to_node, marked_color)
        plotter.refresh()

        return self.drawer.draw(simulation.originating_node,
                                plotter_inst=plotter, arrows=arrows, **draw_kw)

    def __call__(self, simulation, fig=None,
                 every=3, max_frames=None,
                 marked_color='red', arrows=True,
                 repeat_delay=10, **draw_kw):

        def update(path):
            if not path:
                self._plotter.set_node(simulation.originating_node, marked_color)
            else:
                for segment in path:
                    for edge in segment:
                        if arrows:
                            self._plotter.set_edge(edge, marked_color)
                        self._plotter.set_node(edge.from_node, marked_color)
                        self._plotter.set_node(edge.to_node, marked_color)
            self._plotter.refresh()
            return self._plotter.artists

        def gen_func():
            yield None
            for chunk in chunks(simulation.path(max_frames), every):
                yield chunk

        def init():
            self._plotter = self.drawer.draw(simulation.originating_node,
                                             arrows=arrows, **draw_kw)
            return self._plotter.artists

        return FuncAnimation(fig or plt.gcf(), update,
                             frames=gen_func, init_func=init,
                             blit=False, repeat_delay=repeat_delay)


def chunks(iterable, n):
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)

# def chunks(lst, n):
#     """Yield successive n-sized chunks from lst."""
#     for i in range(0, len(lst), n):
#         yield lst[i:i + n]

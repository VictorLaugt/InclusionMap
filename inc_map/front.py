from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pathlib import Path
    from inc_map.back.project import Project
    Node = Path
    Label = str
    Color = tuple[float, float, float]

from inc_map.readable_path import readable_path

import matplotlib.pyplot as plt
import networkx as nx
from netgraph import EditableGraph, InteractiveGraph
from distinctipy import get_colors as get_distinct_colors


def brighten(color: tuple[float, float, float], pastel_factor: float):
    r, g, b = color
    return (
        (r + pastel_factor) / (1. + pastel_factor),
        (g + pastel_factor) / (1. + pastel_factor),
        (b + pastel_factor) / (1. + pastel_factor),
    )


def get_node_color(project: Project) -> tuple[dict[Node, Color], dict[Node, Color]]:
    suffix_to_colors = {path.suffix: None for path in project.source_files}

    distinct_colors = get_distinct_colors(len(suffix_to_colors))
    for suffix, color in zip(suffix_to_colors.keys(), distinct_colors):
        suffix_to_colors[suffix] = color

    return (
        {path: brighten(suffix_to_colors[path.suffix], 2.5) for path in project.source_files},
        {path: suffix_to_colors[path.suffix] for path in project.source_files},
    )


def normalize_positions(node_positions: dict[Node, tuple[float, float]]):
    x_min = y_min = float('inf')
    x_max = y_max = float('-inf')
    for x, y in node_positions.values():
        x_min = min(x, x_min)
        y_min = min(y, y_min)
        x_max = max(x, x_max)
        y_max = max(y, y_max)

    for node in node_positions.keys():
        x, y = node_positions[node]
        node_positions[node] = (
            (x - x_min) / (x_max - x_min),
            (y - y_min) / (y_max - y_min),
        )


def show_project_graph(project: Project, fontsize: float, layout_algorithm: str = None) -> EditableGraph:
    edge_list: list[tuple[Node, Node]] = []
    node_labels: dict[Node, Label] = {}

    for path in project.source_files:
        node_labels[path] = str(readable_path(project.root_dirs, path))
        for required_path in project.dependencies.get_keys(path):
            edge_list.append((required_path, path))

    node_color, node_edge_color = get_node_color(project)

    kwargs = dict(
        arrows=True,

        node_labels=node_labels,
        node_label_fontdict={'size': fontsize},

        node_color=node_color,
        node_edge_color=node_edge_color,
    )

    graph = nx.DiGraph()
    graph.add_nodes_from(project.source_files)
    graph.add_edges_from(edge_list)
    if layout_algorithm:
        node_positions = nx.nx_agraph.graphviz_layout(graph, prog=layout_algorithm)
        normalize_positions(node_positions)
        kwargs['node_layout'] = node_positions

    plot_instance = EditableGraph(graph, **kwargs)
    plt.show()

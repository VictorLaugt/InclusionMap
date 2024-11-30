from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import TypeAlias, TypeVar, Optional
    from pathlib import Path
    from inc_map.back.project import Project
    from re import Pattern
    K = TypeVar('K')
    Node: TypeAlias = Path
    Label: TypeAlias = str
    Color: TypeAlias = tuple[float, float, float]

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


def colorize_distinctly(mapping: dict[K, Color]) -> None:
    distinct_colors = get_distinct_colors(len(mapping))
    for k, color in zip(mapping.keys(), distinct_colors):
        mapping[k] = color


def color_groups_from_suffixes(project: Project) -> tuple[dict[Node, Color], dict[Node, Color]]:
    suffix_to_color = {path.suffix: None for path in project.source_files}
    colorize_distinctly(suffix_to_color)

    node_color = {}
    node_edge_color = {}
    for path in project.source_files:
        color = suffix_to_color[path.suffix]
        node_color[path] = brighten(color, 2.5)
        node_edge_color[path] = color

    return node_color, node_edge_color


def color_groups_from_regexes(project: Project, regexes: list[Pattern]) -> tuple[dict[Node, Color], dict[Node, Color]]:
    file_to_group = {}
    for path in project.source_files:
        filename = path.name
        file_to_group[path] = tuple((pattern.fullmatch(filename) is None) for pattern in regexes)

    group_to_color = {group: None for group in file_to_group.values()}
    colorize_distinctly(group_to_color)

    node_color = {}
    node_edge_color = {}
    for path in project.source_files:
        color = group_to_color[file_to_group[path]]
        node_color[path] = brighten(color, 2.5)
        node_edge_color[path] = color

    return node_color, node_edge_color


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
            (x - x_min) / (x_max - x_min + 1e-6),
            (y - y_min) / (y_max - y_min + 1e-6),
        )


def show_project_graph(
    project: Project,
    fontsize: float,
    group_regexes: list[Pattern],
    layout_algorithm: Optional[str] = None,
) -> EditableGraph:
    edge_list: list[tuple[Node, Node]] = []
    node_labels: dict[Node, Label] = {}

    for path in project.source_files:
        node_labels[path] = str(readable_path(project.root_dirs, path))
        for required_path in project.dependencies.get_keys(path):
            edge_list.append((required_path, path))

    if group_regexes:
        node_color, node_edge_color = color_groups_from_regexes(project, group_regexes)
    else:
        node_color, node_edge_color = color_groups_from_suffixes(project)

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

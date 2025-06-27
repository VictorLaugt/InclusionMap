from __future__ import annotations

from inc_map.back.bimap import BiMap
from inc_map.readable_path import readable_path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Iterator, Collection
    from pathlib import Path
    from inc_map.back.common_features.abstract_inclusion_inspector import AbstractInclusionInspector


def walk(
    directory: Path,
    depth: int,
    extensions: set[str],
    ignore_dirs: set[str]
) -> Iterator[Path]:
    for child in directory.iterdir():
        if child.is_dir() and depth != 0 and child.name not in ignore_dirs:
            yield from walk(child, depth-1, extensions, ignore_dirs)
        elif child.is_file() and child.suffix in extensions:
            yield child


class ProjectBuilder:
    def __init__(self) -> None:
        self.root_dirs: set[Path] = set()
        self.include_dirs: set[Path] = set()

    def add_root_directory(self, new_root: Path) -> None:
        new_root = new_root.resolve()
        sub_roots = [
            root for root in self.root_dirs if root.is_relative_to(new_root)
        ]
        self.root_dirs.difference_update(sub_roots)
        self.root_dirs.add(new_root)

    def add_include_directory(self, inc_dir: Path) -> None:
        inc_dir = inc_dir.resolve()
        sub_idirs = [
            idir for idir in self.include_dirs if idir.is_relative_to(inc_dir)
        ]
        self.include_dirs.difference_update(sub_idirs)
        self.include_dirs.add(inc_dir)

    def build(
        self,
        extensions: set[str],
        ignored_dir_names: set[str],
        InspectorType: Type[AbstractInclusionInspector]
    ) -> Project:
        source_files: set[Path] = set()
        for d in self.root_dirs:
            for f in walk(d, -1, extensions, ignored_dir_names):
                source_files.add(f)

        additional_potential_targets: set[Path] = set()
        for d in self.include_dirs:
            for f in walk(d, -1, extensions, ignored_dir_names):
                additional_potential_targets.add(f)

        inspector = InspectorType(
            source_files | additional_potential_targets,
            self.include_dirs,
            self.root_dirs
        )
        return Project(inspector, source_files, self.root_dirs)


class Project:
    def __init__(self, root_dirs: set[Path], inspector: AbstractInclusionInspector) -> None:
        self.root_dirs = root_dirs  # used to compute more readable paths
        self.source_files: set[Path] = set()  # nodes of the dependency graph
        self.dependencies: BiMap[Path, Path] = BiMap()  # edges of the dependency graph
        self.inspector = inspector  # used to build the edges of the dependency graph

    def build_every_dependencies(self, source_files: Collection[Path]) -> None:
        for file in source_files:
            self.source_files.add(file)
            for dep in self.inspector.find_dependencies(file):
                self.dependencies.add_key_value(file, dep)

    def build_forward_dependencies(self, source_files: Collection[Path]) -> None:
        visited: set[Path] = set()
        layer = source_files
        while len(layer) > 0:
            next_layer = set()
            for file in layer:
                visited.add(file)
                for dep in self.inspector.find_dependencies(file):
                    self.dependencies.add_key_value(file, dep)
                    if dep not in visited:
                        next_layer.add(dep)
            layer = next_layer

        self.source_files.update(visited)

    def build_backward_dependencies(self, source_files: Collection[Path]) -> None:
        visited: set[Path] = set()
        dependencies: BiMap[Path, Path] = BiMap()
        for file in source_files:
            visited.add(file)
            for dep in self.inspector.find_dependencies(file):
                dependencies.add_key_value(file, dep)

        ... # TODO: filter (visited, dependencies) to only keep the backward dependencies; then update (self.source_files, self.dependencies) with (visited, dependencies)
        raise NotImplementedError

    def __repr__(self) -> str:
        string_builder = []
        for file in sorted(self.source_files, key=lambda file: file.name):
            readable_file_path = readable_path(self.root_dirs, file)
            for file_dependency in self.dependencies.get_values(file):
                readable_dependency_path = readable_path(self.root_dirs, file_dependency)
                string_builder.append(
                    f'inclusion : {readable_file_path} -> {readable_dependency_path}'
                )
        return '\n'.join(string_builder)

    def is_not_empty(self) -> bool:
        return len(self.dependencies.keys()) > 0

    def remove_redundancies(self) -> None:
        for a in self.source_files:
            a_redundant_include = []
            a_dependencies = self.dependencies.get_values(a)

            for b in a_dependencies:
                if (b_dependencies := self.dependencies.get_values(b)):
                    for c in (redundancy := b_dependencies & a_dependencies):
                        print(
                            f"simplified : {readable_path(self.root_dirs, a)} -> "
                            f"{readable_path(self.root_dirs, b)} -> {readable_path(self.root_dirs, c)}"
                        )
                    a_redundant_include.extend(redundancy)

            for c in a_redundant_include:
                self.dependencies.discard_key_value(a, c)

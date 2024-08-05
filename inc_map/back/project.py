from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Iterator, Iterable, Hashable
    from pathlib import Path
    from inc_map.back.abstract_inclusion_inspector import AbstractInclusionInspector

from inc_map.readable_path import readable_path

class BiMap:
    def __init__(self):
        self._key_to_values: dict[Hashable, set[Hashable]] = {}
        self._value_to_keys: dict[Hashable, set[Hashable]] = {}

    def add_key_value(self, key: Hashable, value: Hashable):
        if (value_set := self._key_to_values.get(key)) is not None:
            value_set.add(value)
        else:
            self._key_to_values[key] = {value}

        if (key_set := self._value_to_keys.get(value)) is not None:
            key_set.add(key)
        else:
            self._value_to_keys[value] = {key}

    def discard_key_value(self, key: Hashable, value: Hashable):
        value_set = self._key_to_values.get(key)
        key_set = self._value_to_keys.get(value)
        if value_set is not None and key_set is not None:
            value_set.discard(value)
            key_set.discard(key)

    def contains_key_value(self, key, value) -> bool:
        if (value_set := self._key_to_values.get(key)) is None:
            return False
        if (key_set := self._value_to_keys.get(value)) is None:
            return False
        return value in value_set and key in key_set

    def get_values(self, key: Hashable) -> set[Hashable]:
        if (value_set := self._key_to_values.get(key)) is None:
            return ()
        return value_set

    def get_keys(self, value: Hashable) -> set[Hashable]:
        if (key_set := self._value_to_keys.get(value)) is None:
            return ()
        return key_set

    def values(self) -> Iterable[Hashable]:
        return self._key_to_values.values()

    def keys(self) -> Iterable[Hashable]:
        return self._key_to_values.keys()


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
    def __init__(self):
        self.root_dirs: set[Path] = set()
        self.include_dirs: list[Path] = []

    def add_root_directory(self, new_root: Path):
        new_root = new_root.resolve()
        sub_roots = [
            root for root in self.root_dirs if root.is_relative_to(new_root)
        ]
        self.root_dirs.difference_update(sub_roots)
        self.root_dirs.add(new_root)

    def add_include_directory(self, inc_dir: Path):
        self.add_root_directory(inc_dir)
        self.include_dirs.append(inc_dir.resolve())

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
        inspector = InspectorType(source_files, self.include_dirs, self.root_dirs)
        return Project(inspector, source_files, self.root_dirs)


class Project:
    def __init__(
        self,
        inspector: AbstractInclusionInspector,
        source_files: set[Path],
        root_dirs: set[Path],
    ) -> None:
        self.source_files = source_files
        self.root_dirs = root_dirs

        self.dependencies: BiMap[Path, Path] = BiMap()
        for file in self.source_files:
            for dep in inspector.find_dependencies(file):
                self.dependencies.add_key_value(file, dep)

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

    def readable_path(self, file: Path) -> Path:
        for root in self.root_dirs:
            if file.is_relative_to(root):
                if len(self.root_dirs) == 1:
                    return file.relative_to(root)
                return Path(root.name, file.relative_to(root))
        raise ValueError(f'Unknown file "{file}"')

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

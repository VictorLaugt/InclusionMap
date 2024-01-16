from __future__ import annotations
from typing import Iterable, Iterator, Hashable

import sys
from pathlib import Path

from inclusion_map.back.inclusion_instructions import InclusionInstructionMatcher
from inclusion_map.back.target_parser import TargetParser


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


def walk(directory: Path, depth: int,
         extensions: set[str], ignore_dirs: set[str]) -> Iterator[Path]:
    """Itère récursivement sur tous les fichiers du répertoire `directory` et
    ses sous répertoires, sauf ceux dont le nom est dans `ignore_dirs`, jusqu'à
    une profondeur maximale de `depth` (-1 pour n'avoir aucune limite).
    N'itère que sur les fichiers dont l'extension est présente dans l'ensemble
    `extensions`.
    """
    for child in directory.iterdir():
        if child.is_dir() and depth != 0 and child.name not in ignore_dirs:
            yield from walk(child, depth-1, extensions, ignore_dirs)
        elif child.is_file() and child.suffix in extensions:
            yield child


class Project:
    """
    Attributs
    ---------
    root_dirs: list[Path]
        Chemins absolus des répertoires racines du projet.  Les fichiers sources
        du projets sont tous contenus dans les répertoires racines ou leurs
        sous-répertoires.

    include_dirs: list[Path]
        Chemins absolus des répertoires dans lesquels rechercher les fichiers
        ciblés par les instructions d'inclusion.

    files: set[Path]
        Chemins absolus des fichiers sources du projet.

    dependencies: BiMap[Path, Path]
        BiMap qui, à un fichier source du projet, associe tous les fichiers
        sources dont il dépend.

    inc_matcher: InclusionInstructionMatcher
        Objet permettant de trouver les instructions d'inclusion dans les codes
        sources.

    target_parser_type: type  #issubclass(target_parser, TargetParser)
        Type des objets permettant d'interpréter les instructions d'inclusion
        pour comprendre à quels autres fichiers elles font référence.
    """

    def __init__(self, inclusion_matcher, target_parser_type):
        self.root_dirs: list[Path] = []
        self.include_dirs: list[Path] = []
        self.files: set[Path] = set()
        self.dependencies: BiMap[Path, Path] = BiMap()

        self.inc_matcher: InclusionInstructionMatcher = inclusion_matcher  # testé
        self.target_parser_type: type = target_parser_type  # TODO: tester target_parser.py

    def __repr__(self) -> str:
        string_builder = []
        for code_file in sorted(self.files, key = lambda file: file.name):
            code_file_path = self.readable_path(code_file)
            for required_code_file in self.dependencies.get_values(code_file):
                required_code_file_path = self.readable_path(required_code_file)
                string_builder.append(
                    f'inclusion : {code_file_path} -> {required_code_file_path}'
                )
        # string_builder.append(')')
        return '\n'.join(string_builder)

    def _warning_in_file(self, code_file: Path, line_no: int, message: str):
        print(f"{message} : {self.readable_path(code_file)}:{line_no}",
              file=sys.stderr)

    def _find_file_dependencies(self, file: Path, target_parser: TargetParser):
        with file.open(mode='r') as source_code:
            for line_no, line in enumerate(source_code):
                for target in self.inc_matcher.targets(line):
                    if (required_file := target_parser.parse(target)) is None:
                        self._warning_in_file(
                            file, line_no, f'target not found "{target}"')
                    else:
                        self.dependencies.add_key_value(file, required_file)

    def readable_path(self, code_file: Path) -> Path:
        for root in self.root_dirs:
            if code_file.is_relative_to(root):
                if len(self.root_dirs) == 1:
                    return code_file.relative_to(root)
                return Path(root.name, code_file.relative_to(root))
        raise ValueError(f'Unknown file "{code_file}"')

    def add_root_directory(self, new_root: Path):
        """Ajoute le chemin absolu `new_root` à la liste des répertoires racines
        du projet.
        """
        new_root = new_root.resolve()
        for i, root in enumerate(self.root_dirs):
            if root.is_relative_to(new_root):
                self.root_dirs[i] = new_root
                return
        self.root_dirs.append(new_root)

    def add_include_directory(self, directory: Path):
        """Ajoute le chemin absolu `directory` à la liste des répertoires dans
        lesquels rechercher les fichiers ciblés par les instructions d'inclusion.
        """
        self.include_dirs.append(directory.resolve())

    def find_source_files(self, extensions: set[str], ignore_dirs: set[str]):
        """Trouve tous les fichiers sources du projet en les cherchant depuis
        les répertoires racines du projet.
        """
        for d in self.root_dirs:
            for f in walk(d, -1, extensions, ignore_dirs):
                self.files.add(Path(f))

    def find_dependencies(self):
        """Analyse les instructions d'inclusions présentent dans les fichiers
        sources du projet pour trouver toutes les dépendances entre eux.
        Pendant l'analyse, lève un warning pour chaque instruction d'inclusion
        faisant référence à un fichier inconnu.
        """
        target_parser = self.target_parser_type(self.files, self.include_dirs)
        for code_file in self.files:
            self._find_file_dependencies(code_file, target_parser)

    def remove_redundancies(self):  # TODO: tester remove_redundancies
        """Pour chaque triplet de fichiers sources distincts (a, b, c) du projet,
        Si a inclut b, b inclut c, et a inclut c,
        alors supprime l'information que a inclu c
        """
        for a in self.files:
            a_redundant_include = []
            a_dependencies = self.dependencies.get_values(a)

            for b in a_dependencies:
                if (b_dependencies := self.dependencies.get_values(b)):
                    a_redundant_include.extend(b_dependencies & a_dependencies)

            for c in a_redundant_include:
                self.dependencies.discard_key_value(a, c)
                print(
                    f"simplified : {self.readable_path(a)} -> "
                    f"{self.readable_path(b)} -> {self.readable_path(c)}"
                )

    def is_not_empty(self) -> bool:
        """Renvoie True s'il y a au moins une instruction d'inclusion d'un
        fichier du projet vers un autre fichier du projet.
        """
        return len(self.dependencies.keys()) > 0

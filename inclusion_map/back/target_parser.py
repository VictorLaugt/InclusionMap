from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable

from itertools import chain

from pathlib import Path

__all__ = (
    'TargetParser', 'CTargetParser', 'PythonTargetParser'
)


class TargetParser(ABC):
    """La cible d'une instruction d'inclusion désigne un ou plusieurs fichiers
    du projet.

    Une instance de TargetParser est un objet capable de comprendre, pour un
    un certain langage programmation fixé, quels sont les fichiers sources
    désignés par la cible d'une instruction d'inclusion.

    Exemples:
     - En C/C++, si le code est compilé avec l'option `-I foo` et que le
    répertoire foo contient un fichier bar.h, alors la cible "bar.h" de
    l'instruction `#include "bar.h"` désigne le fichier "foo/bar.h".

    Attributs
    ---------
    files: set[Path]
        Chemins absolus des fichiers sources du projet.

    include_dirs: list[Path]
        Chemins absolus des répertoires dans lesquels rechercher les fichiers
        ciblés par les instructions d'inclusions.
    """

    def __init__(self, files, include_dirs):
        self.files: set[Path] = files
        self.include_dirs: list[Path] = include_dirs

    @abstractmethod
    def parse(self, target: str, relative_to: list[Path] = None) -> Path | None:
        """Renvoie le chemin vers le fichier source désigné par la cible
        `target` d'une instruction d'inclusion.  Renvoie None si le fichier
        source n'est pas trouvé.
        """


class ClassicTargetParser(TargetParser):
    def search_in_include_dirs(self, target_path: Path) -> Path | None:
        for include_directory in self.include_dirs:
            candidate_path = include_directory.joinpath(target_path)
            if candidate_path in self.files:
                return candidate_path


class CTargetParser(ClassicTargetParser):
    def parse(self, target: str, _ = None) -> Path | None:
        return self.search_in_include_dirs(Path(target))


class PythonTargetParser(ClassicTargetParser):
    @staticmethod
    def backward(directory: Path, n: int) -> Path | None:
        back = 0
        for parent_directory in directory.parents:
            if back == n:
                return parent_directory
            back += 1
        return None

    @staticmethod
    def target_to_paths(target: str) -> tuple[Path, Path]:
        path = Path(*target.split('.'))
        return (path.with_suffix('.py'), path.joinpath('__init__.py'))

    def search_relative_to(self, target: str, relative_to: Iterable[Path]) -> Path | None:
        back = 0
        while target[back] == '.':
            back += 1
        target_as_file, target_as_package = self.target_to_paths(target[back:])

        for reference_dir in relative_to:
            if (include_dir := self.backward(reference_dir, back)) is not None:
                if (candidate := include_dir.joinpath(target_as_file)) in self.files:
                    return candidate
                if (candidate := include_dir.joinpath(target_as_package)) in self.files:
                    return candidate

    def parse(self, target: str, relative_to: list[Path] = None) -> Path | None:
        if relative_to:
            return self.search_relative_to(target, relative_to)
        else:
            target_as_file, target_as_package = self.target_to_paths(target)
            return (
                self.search_in_include_dirs(target_as_file) or
                self.search_in_include_dirs(target_as_package)
            )

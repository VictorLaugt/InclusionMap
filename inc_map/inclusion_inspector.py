from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Iterable, Sequence
    from pathlib import Path

import abc

class AbstractInclusionInspector(abc.ABC):
    def __init__(self, source_files: Sequence[Path], include_dirs: Sequence[Path]) -> None:
        self.source_files = source_files
        self.include_dirs = include_dirs

    def search_in_include_dirs(self, target_path: Path) -> Optional[Path]:
        for include_directory in self.include_dirs:
            candidate_path = include_directory.joinpath(target_path)
            if candidate_path in self.source_files:
                return candidate_path

    @abc.abstractmethod
    def find_dependencies(self, file: Path) -> Iterable[Path]:
        pass


from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Container, Iterable, Collection, Sequence
    from pathlib import Path
    from inc_map.back.abstract_inclusion_instruction import AbstractInclusionInstruction

from inc_map.readable_path import readable_path

import sys
import abc

class AbstractInclusionInspector(abc.ABC):
    def __init__(self, source_files: Container[Path], include_dirs: Sequence[Path], root_dirs: Collection[Path]) -> None:
        self.root_dirs = root_dirs
        self.source_files = source_files
        self.include_dirs = include_dirs

    def warning(
        self,
        message:str,
        file: Path,
        instruction: AbstractInclusionInstruction
    ) -> None:
        print((
                f"{message} : {readable_path(self.root_dirs, file)}:"
                f"{instruction.line_n}: {instruction}"
            ), file=sys.stderr
        )

    def warning_not_found(
        self,
        file: Path,
        instruction: AbstractInclusionInstruction
    ) -> None:
        self.warning("target not found", file, instruction)

    def search_in_include_dirs(self, target_path: Path) -> Optional[Path]:
        for include_directory in self.include_dirs:
            candidate_path = include_directory.joinpath(target_path)
            if candidate_path in self.source_files:
                return candidate_path

    @abc.abstractmethod
    def find_dependencies(self, file: Path) -> Iterable[Path]:
        pass


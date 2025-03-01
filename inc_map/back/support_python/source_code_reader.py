from __future__ import annotations

import ijson
import abc

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Optional
    from pathlib import Path


class AbstractPythonFileReader(abc.ABC):
    @abc.abstractmethod
    def iter_code_cells(self) -> Iterable[tuple[Optional[int], str]]:
        pass


class StandardPythonFileReader(AbstractPythonFileReader):
    def __init__(self, file: Path) -> None:
        self.file = file

    def iter_code_cells(self) -> Iterable[tuple[None, str]]:
        with self.file.open(mode='r') as f:
            yield None, f.read()


class PythonNotebookReader(AbstractPythonFileReader):
    def __init__(self, file: Path) -> None:
        self.file = file

    def iter_code_cells(self) -> Iterable[tuple[int, str]]:
        with self.file.open(mode='r', encoding='utf-8') as f:
            for i, cell in enumerate(ijson.items(f, 'cells.item'), start=1):
                code = cell.get('source')
                if cell.get('cell_type') == 'code' and code is not None:
                    yield i, code

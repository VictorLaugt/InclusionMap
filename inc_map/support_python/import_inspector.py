from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    ...

from inc_map.inclusion_inspector import AbstractInclusionInspector
from inc_map.support_python.import_matcher import find_imports

class ImportInspector(AbstractInclusionInspector):
    def parse

    def find_dependencies(self, file: Path) -> Iterable[Path]:
        with file.open(mode='r') as f:
            source_code = f.read()
            for instruction in find_imports(source_code):
                ...

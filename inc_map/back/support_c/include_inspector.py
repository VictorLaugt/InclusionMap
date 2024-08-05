from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from typing import Optional
    from inc_map.back.support_c.include_matcher import IncludeInstruction

import sys
from pathlib import Path

from inc_map.back.abstract_inclusion_inspector import AbstractInclusionInspector
from inc_map.back.support_c.include_matcher import IncludeMatcher


class IncludeInspector(AbstractInclusionInspector):
    def parse_include(self, instruction: IncludeInstruction) -> Optional[Path]:
        included_path = Path(*instruction.included.split('/'))
        return self.search_in_include_dirs(included_path)

    def find_dependencies(self, file: Path) -> Iterable[Path]:
        with file.open(mode='r') as f:
            include_matcher = IncludeMatcher(f.read())

        for instruction in include_matcher.find_include_instructions():
            target = self.parse_include(instruction)
            if target is not None:
                if target.suffix in ('.c', '.cpp', '.cxx'):
                    self.warning("target is not a header", file, instruction)
                yield target
            else:
                self.warning_not_found(file, instruction)

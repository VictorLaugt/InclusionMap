from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Iterable
    from inc_map.back.support_python.import_matcher import ImportInstruction, FromImportInstruction

import sys
from pathlib import Path

from inc_map.back.abstract_inclusion_inspector import AbstractInclusionInspector
from inc_map.back.support_python.import_matcher import ImportMatcher


class ImportInspector(AbstractInclusionInspector):
    def solve_relative_import_base(self, queue: str, file: Path) -> Optional[Path]:
        back = 0
        while back < len(queue) and queue[back] == '.':
            back += 1

        reference_dir = file
        for _ in range(back):
            if len(reference_dir.parts) == 0:
                return
            reference_dir = reference_dir.parent

        return reference_dir.joinpath(queue[back:])

    def parse_from_import(self, instruction: FromImportInstruction, file: Path) -> Iterable[Path]:
        if instruction.queue.startswith('.'):
            base = self.solve_relative_import_base(instruction.queue, file)
            if base is None:
                return
        else:
            base = Path(*instruction.queue.split('.'))

        for h in instruction.heads:
            target = (
                self.search_in_include_dirs(base.with_suffix('.py')) or              # from file import member
                self.search_in_include_dirs(base.joinpath(h).with_suffix('.py')) or  # from directory import file
                self.search_in_include_dirs(base.joinpath('__init__.py'))            # from directory import member
            )
            if target is None:
                self.warning_not_found(file, instruction)
            else:
                yield target

    def parse_import(self, instruction: ImportInstruction, file: Path) -> Iterable[Path]:
        for q in instruction.queues:
            p = Path(*q.split('.'))
            target = (
                self.search_in_include_dirs(p.with_suffix('.py')) or    # import file
                self.search_in_include_dirs(p.joinpath('__init__.py'))  # import directory
            )
            if target is None:
                self.warning_not_found(file, instruction)
            else:
                yield target


    def find_dependencies(self, file: Path) -> Iterable[Path]:
        with file.open(mode='r') as f:
            import_matcher = ImportMatcher(f.read())

        for instruction in import_matcher.find_import_instructions():
            yield from self.parse_import(instruction, file)
        for instruction in import_matcher.find_from_import_instructions():
            yield from self.parse_from_import(instruction, file)

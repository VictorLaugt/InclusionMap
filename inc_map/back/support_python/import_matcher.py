from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Sequence

from dataclasses import dataclass

import numpy as np
import re

from inc_map.back.abstract_inclusion_instruction import AbstractInclusionInstruction


REGEX_COMMENT = re.compile(r'#.*\n')

LST = r'\w+([^\S\n]*,[^\S\n]*\w+)*'  # comma-separated list of words on a single line
MULTI_LINE_LST = r'\w+(\s*,\s*\w+)*\s*,?'    # comma-separated list of words on multiple lines

REGEX_IMPORT = re.compile(
    fr'\nimport[^\S\n]+(?P<queues>{LST})'
)
REGEX_FROM_IMPORT_LST = re.compile(
    fr'\nfrom[^\S\n]+(?P<queue>[\.\w]+?)[^\S\n]+import[^\S\n]+(?P<heads>{LST})'
)
REGEX_FROM_IMPORT_PARLST = re.compile(
    fr'\nfrom[^\S\n]+(?P<queue>[\.\w]+?)[^\S\n]+import[^\S\n]+\(\s*(?P<heads>{MULTI_LINE_LST})\s*\)'
)


def without_comment(source_code: str) -> str:
    return REGEX_COMMENT.sub('\n', source_code)


@dataclass
class ImportInstruction(AbstractInclusionInstruction):
    """import `queues`"""
    line_n: int
    queues: Sequence[str]

    def __repr__(self) -> str:
        return f"import {', '.join(self.queues)}"


@dataclass
class FromImportInstruction(AbstractInclusionInstruction):
    """from `queue` import `heads`"""
    line_n: int
    queue: str
    heads: Sequence[str]

    def __repr__(self) -> str:
        return f"from {self.queue} import {', '.join(self.heads)}"


class ImportMatcher:
    def __init__(self, source_code: str) -> None:
        source_code = without_comment(f"\n{source_code}\n")

        line_indices = np.empty(len(source_code), dtype=np.uint32)
        new_line_count = 0
        for i, c in enumerate(source_code):
            if c == '\n':
                new_line_count += 1
                line_indices[i] = new_line_count

        self.source_code = source_code
        self.line_indices = line_indices


    def find_import_instructions(self) -> Iterable[ImportInstruction]:
        for import_match in REGEX_IMPORT.finditer(self.source_code):
            yield ImportInstruction(
                line_n=self.line_indices[import_match.start()]+1,
                queues=[q.strip() for q in import_match.group('queues').split(',')]
            )

    def find_from_import_instructions(self) -> Iterable[FromImportInstruction]:
        for from_import_match in REGEX_FROM_IMPORT_LST.finditer(self.source_code):
            yield FromImportInstruction(
                line_n=self.line_indices[from_import_match.start()]+1,
                queue=from_import_match.group('queue'),
                heads=[h.strip() for h in from_import_match.group('heads').split(',')]
            )
        for from_import_match in REGEX_FROM_IMPORT_PARLST.finditer(self.source_code):
            yield FromImportInstruction(
                line_n=self.line_indices[from_import_match.start()]+1,
                queue=from_import_match.group('queue'),
                heads=[h.strip() for h in from_import_match.group('heads').split(',')]
            )

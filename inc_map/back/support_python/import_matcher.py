from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Sequence

from dataclasses import dataclass

import numpy as np
import re

from inc_map.back.common_features.abstract_inclusion_instruction import AbstractInclusionInstruction


REGEX_COMMENT = re.compile(r'#.*\n')

SPACE = r'[^\S\n]*'  # sequence of spacing characters (excluding line break)
MULTI_LINE_SPACE = r'\s*'  # sequence of spacing characters (inclucing line break)

WORD = r'\w+'  # non-empty sequence of letters
DOTTED_WORD = r'[\w\.]+'  # non-empty sequence of letters or dots

HEAD = fr'{WORD}({SPACE}as{SPACE}{WORD})?'
D_HEAD = fr'{DOTTED_WORD}({SPACE}as{SPACE}{WORD})?'
ML_HEAD = fr'{WORD}({MULTI_LINE_SPACE}as{MULTI_LINE_SPACE}{WORD})?'

HEAD_LST = fr'{HEAD}({SPACE},{SPACE}{HEAD})*'  # comma-separated list of heads on a single line
DOTTED_HEAD_LST = fr'{D_HEAD}({SPACE},{SPACE}{D_HEAD})*'  # comma-separated list of dotted heads on a single line
HEAD_MULTI_LINE_LST = fr'{ML_HEAD}({MULTI_LINE_SPACE},{MULTI_LINE_SPACE}{ML_HEAD})*{MULTI_LINE_SPACE},?'  # comma-separated list of heads on multiple lines

REGEX_QUEUE = re.compile(
    fr'(?P<queue>{DOTTED_WORD})({SPACE}as{SPACE}{WORD})?'
)
REGEX_IMPORT = re.compile(
    fr'\nimport[^\S\n]+(?P<queues>{DOTTED_HEAD_LST})'
)
REGEX_FROM_IMPORT_LST = re.compile(
    fr'\nfrom[^\S\n]+(?P<queue>[\.\w]+?)[^\S\n]+import[^\S\n]+(?P<heads>\*|({HEAD_LST}))'
)
REGEX_FROM_IMPORT_PARLST = re.compile(
    fr'\nfrom[^\S\n]+(?P<queue>[\.\w]+?)[^\S\n]+import[^\S\n]+\(\s*(?P<heads>{HEAD_MULTI_LINE_LST})\s*\)'
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
            queues = []
            for q in import_match.group('queues').split(','):
                queues.append(REGEX_QUEUE.fullmatch(q.strip()).group('queue'))
            yield ImportInstruction(
                line_n=self.line_indices[import_match.start()],
                queues=queues
            )

    def find_from_import_instructions(self) -> Iterable[FromImportInstruction]:
        for from_import_match in REGEX_FROM_IMPORT_LST.finditer(self.source_code):
            yield FromImportInstruction(
                line_n=self.line_indices[from_import_match.start()],
                queue=from_import_match.group('queue'),
                heads=[h.strip() for h in from_import_match.group('heads').split(',')]
            )
        for from_import_match in REGEX_FROM_IMPORT_PARLST.finditer(self.source_code):
            yield FromImportInstruction(
                line_n=self.line_indices[from_import_match.start()],
                queue=from_import_match.group('queue'),
                heads=[h.strip() for h in from_import_match.group('heads').split(',')]
            )

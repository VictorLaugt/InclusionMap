from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Sequence

from dataclasses import dataclass
import re


REGEX_COMMENT = re.compile(r'#.*\n')

LST = r'\w+([^\S\n]*,[^\S\n]*\w+)*'
PARLST = r'\(\s*\w+(\s*,\s*\w+)*\s*,?\s*\)'

REGEX_IMPORT = re.compile(
    fr'\nimport[^\S\n]+(?P<queues>{LST})'
)

REGEX_FROM_IMPORT = re.compile(
    fr'\nfrom[^\S\n]+(?P<queue>[\.\w]+?)[^\S\n]+import[^\S\n]+(?P<heads>({LST})|({PARLST}))'
)


@dataclass
class ImportInstruction:
    """import <queues>"""
    queues: Sequence[str]


@dataclass
class FromImportInstruction:
    """from <queue> import <heads>"""
    queue: str
    heads: Sequence[str]

def without_comments(source_code: str) -> str:
    return REGEX_COMMENT.sub('\n', source_code)


def solve(source_code: str) -> Iterable[ImportInstruction | FromImportInstruction]:
    source_code = without_comments(f"\n{source_code}\n")

    for import_match in REGEX_IMPORT.finditer(source_code):
        yield ImportInstruction(
            queues=[q.strip() for q in import_match.group('queues').split(',')]
        )

    for from_import_match in REGEX_FROM_IMPORT.finditer(source_code):
        yield FromImportInstruction(
            queue=from_import_match.group('queue'),
            heads=[h.strip() for h in from_import_match.group('heads').split(',')]
        )

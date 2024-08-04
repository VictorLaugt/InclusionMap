from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Sequence

from dataclasses import dataclass
import re

__all__ = ('find_imports',)


REGEX_COMMENT = re.compile(r'#.*\n')

LST = r'\w+([^\S\n]*,[^\S\n]*\w+)*'          # comma-separated list of words on a single line
PARLST = r'\(\s*\w+(\s*,\s*\w+)*\s*,?\s*\)'  # parenthesized comma-separated list of words on multiple lines

REGEX_IMPORT = re.compile(
    fr'\nimport[^\S\n]+(?P<queues>{LST})'
)
REGEX_FROM_IMPORT = re.compile(
    fr'\nfrom[^\S\n]+(?P<queue>[\.\w]+?)[^\S\n]+import[^\S\n]+(?P<heads>({LST})|({PARLST}))'
)


@dataclass
class ImportInstruction:
    """import `queues`"""
    line_nb: int
    queues: Sequence[str]


@dataclass
class FromImportInstruction:
    """from `queue` import `heads`"""
    line_nb: int
    queue: str
    heads: Sequence[str]


def without_comments(source_code: str) -> str:
    return REGEX_COMMENT.sub('\n', source_code)


def find_imports(source_code: str) -> Iterable[ImportInstruction | FromImportInstruction]:
    source_code = without_comments(f"\n{source_code}\n")

    for import_match in REGEX_IMPORT.finditer(source_code):
        yield ImportInstruction(
            line_nb=...,
            queues=[q.strip() for q in import_match.group('queues').split(',')]
        )

    for from_import_match in REGEX_FROM_IMPORT.finditer(source_code):
        yield FromImportInstruction(
            line_nb=...,
            queue=from_import_match.group('queue'),
            heads=[h.strip() for h in from_import_match.group('heads').split(',')]
        )

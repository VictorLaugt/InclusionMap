from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Sequence

from dataclasses import dataclass

import numpy as np
import re


REGEX_COMMENT = re.compile(r'//.*\n')

REGEX_LIBRARY_INCLUDE = re.compile(r'\n#\s*include\s*"(?P<included>.*)"')
REGEX_INTERNAL_INCLUDE = re.compile(r'\n#\s*include\s*<(?P<included>.*)>')


def without_comment(source_code: str) -> str:
    return REGEX_COMMENT.sub('\n', source_code)


@dataclass
class IncludeInstruction:
    internal: bool
    line_n: int
    included: str

    def __repr__(self) -> str:
        if self.internal:
            return f'#include "{self.included}"'
        return f'#include <{self.included}>'


class IncludeMatcher:
    def __init__(self, source_code: str) -> None:
        source_code = without_comment(f"\n{source_code}\n")

        line_indices = np.full(len(source_code), -1, dtype=np.uint32)
        new_line_count = 0
        for i, c in enumerate(source_code):
            if c == '\n':
                new_line_count += 1
                line_indices[i] = new_line_count

        self.source_code = source_code
        self.line_indices = line_indices

    def find_include_instructions(self) -> Iterable[IncludeInstruction]:
        for include_match in REGEX_INTERNAL_INCLUDE.finditer(self.source_code):
            yield IncludeInstruction(
                internal=True,
                line_n=self.line_indices[include_match.start()]+1,
                included=include_match.group('included')
            )
        for include_match in REGEX_LIBRARY_INCLUDE.finditer(self.source_code):
            yield IncludeInstruction(
                internal=False,
                line_n=self.line_indices[include_match.start()]+1,
                included=include_match.group('included')
            )

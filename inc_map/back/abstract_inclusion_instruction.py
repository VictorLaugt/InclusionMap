from __future__ import annotations

from dataclasses import dataclass
import abc

@dataclass
class AbstractInclusionInstruction(abc.ABC):
    line_n: int

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

from __future__ import annotations

import abc


class AbstractInclusionInstruction(abc.ABC):
    @abc.abstractmethod
    def code_location(self) -> str:
        pass

    @abc.abstractmethod
    def code_repr(self) -> str:
        pass

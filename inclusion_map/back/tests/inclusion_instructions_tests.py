import unittest

from inclusion_map.back.inclusion_instructions import c_include_matcher, python_import_matcher

__all__ = (
    "TestCIncludeMatcher", "TestPythonImportMatcher"
)


class TestInclusionInstructionMatcher(unittest.TestCase):
    def _test_instruction_set(self, *instructions):
        for inst, expected in instructions:
            self.assertTupleEqual(
                tuple(self.matcher.targets(inst)),
                expected
            )


class TestCIncludeMatcher(TestInclusionInstructionMatcher):
    matcher = c_include_matcher

    def test_match_include(self):
        self._test_instruction_set(
            ('# include  "core.h"', ('core.h',)),
            ('#include "physic/dynamic.h"', ('physic/dynamic.h',)),
            ('#include <stdlib.h>', ('stdlib.h',)),
            ('#include <sys/types.h>', ('sys/types.h',)),
        )


class TestPythonImportMatcher(TestInclusionInstructionMatcher):
    matcher = python_import_matcher

    def test_match_relative_from_import(self):
        self._test_instruction_set(
            ("from .foo.bar import nano", (".foo.bar",)),
            ("from .foo import bar", (".foo",)),
            ("from . import zoo", (".",)),
            ("from ..boo import noob", ("..boo",)),
            ("from ...toto import tata", ("...toto",)),
            ("from ..papala import *", ("..papala",)),
        )

    def test_match_absolute_from_import(self):
        self._test_instruction_set(
            ("from sympy.core.relational import Eq", ("sympy.core.relational",)),
            ("from chess import Board as ChessBoard", ("chess",)),
            ("from front import display, refresh_window", ("front",)),
        )

    def test_match_absolute_import(self):
        self._test_instruction_set(
            ("import moula.ga", ("moula.ga",)),
            ("import moula,ga", ("moula", "ga")),
            ("import matplotlib.pyplot as plt", ("matplotlib.pyplot",)),
            ("import math, numpy as np, __hello__", ("math", "numpy", "__hello__")),
            ('import matplotlib; matplotlib.use("Qt5Agg")', ('matplotlib',)),
        )

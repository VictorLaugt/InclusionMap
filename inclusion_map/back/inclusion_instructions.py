from __future__ import annotations
from typing import Iterable
from abc import ABC, abstractmethod

import re

__all__ = (
    'InclusionInstructionMatcher', 'c_include_matcher', 'python_import_matcher'
)


class InclusionInstructionMatcher(ABC):
    """Une instruction d'inclusion est, de manière générale, une instruction
    qui rend dépendant un fichier d'un autre dans un projet.

    Une instance de InclusionInstructionMatcher est un objet capable de
    reconnaitre les instructions d'inclusion d'un certain langage de
    programmation fixé et d'en extraire les cibles.

    Exemples:
     - En C/C++, l'instruction `#include "my_module.h"` a pour cible "my_module.h".
     - En Python, l'instruction `from my_package.my_module import stuff` a pour
     cible "my_package.my_module'.
     - En Python, l'instruction `import foo, bar` a pour cibles "foo" et "bar".
    """
    @abstractmethod
    def targets(self, line: str) -> Iterable[str]:
        """Si la ligne de code `line` est une instruction d'inclusion, alors
        renvoie un itérable contenant ses cibles. Sinon, renvoie un itérable
        vide.
        """


class ClassicInclusionMatcher(InclusionInstructionMatcher):
    comment_regex_list: list[re.Pattern]
    include_regex_list: list[re.Pattern]

    def strip_comment(self, line: str) -> str:
        for comment_regex in self.comment_regex_list:
            line = comment_regex.sub('', line)
        return line

    def match_targets_block(self, line: str) -> str | None:
        line = self.strip_comment(line)
        for include_regex in self.include_regex_list:
            if (include_match := include_regex.match(line)) is not None:
                return include_match.group('targets_block')


class CIncludeMatcher(ClassicInclusionMatcher):
    comment_regex_list = (re.compile(r'\s*//.*$'),)
    include_regex_list = (
        re.compile(r'^\s*#\s*include\s*"(?P<targets_block>.*)"'),
        re.compile(r'^\s*#\s*include\s*<(?P<targets_block>.*)>'),
    )

    def targets(self, line: str) -> Iterable[str]:
        if (target := self.match_targets_block(line)) is not None:
            return (target,)
        else:
            return ()


class PythonImportMatcher(ClassicInclusionMatcher):
    comment_regex_list = (re.compile(r'\s*#.*$'),)
    include_regex_list = (
        re.compile(r'import\s*(?P<targets_block>.*?)\s*;.*'),
        re.compile(r'import\s*(?P<targets_block>.*)'),
        re.compile(r'from\s*(?P<targets_block>.*?)\s*import.*'),  #FIXME: should match "from importlib.metadata import version"
    )
    targets_separator = re.compile('\s*,\s*')
    rename_syntax = re.compile(r'^(?P<target>.*?)\sas.*')

    @classmethod
    def target_real_name(cls, target: str) -> str:
        if (real_name_match := cls.rename_syntax.match(target)) is not None:
            return real_name_match.group('target')
        else:
            return target

    def targets(self, line):
        if (targets_block := self.match_targets_block(line)) is not None:
            return [
                self.target_real_name(target) for target in
                self.targets_separator.split(targets_block)
            ]
        else:
            return ()


c_include_matcher = CIncludeMatcher()
python_import_matcher = PythonImportMatcher()

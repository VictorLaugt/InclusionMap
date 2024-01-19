from pathlib import Path
from typing import Iterable
import unittest

from inclusion_map.back.project_dependencies import Project
from inclusion_map.back.inclusion_instructions import InclusionInstructionMatcher
from inclusion_map.back.target_parser import TargetParser


class InclusionInstructionMatcherMock(InclusionInstructionMatcher):
    def targets(self, line: str) -> Iterable[str]:
        return ()


class TargetParserMock(TargetParser):
    def __init__(self, files, include_dirs):
        pass

    def parse(self, target: str, relative_to: list[Path] = None) -> Path | None:
        pass


class StructuralTestProject(unittest.TestCase):
    def new_project(self, nodes, edges):
        p = Project(InclusionInstructionMatcherMock(), TargetParserMock)
        p.root_dirs.add(Path())
        p.include_dirs.append(Path())

        for n in nodes:
            p.files.add(Path(str(n)))

        for a, b in edges:
            p.dependencies.add_key_value(Path(str(a)), Path(str(b)))

        return p

    def assertHasNoDependency(self, project, file, required_file):
        self.assertTrue(
            Path(str(required_file)) not in project.dependencies.get_values(
                Path(str(file)))
        )

    def assertHasDependency(self, project, file, required_file):
        self.assertTrue(
            Path(str(required_file)) in project.dependencies.get_values(
                Path(str(file)))
        )

    def test_remove_redundancies_classic(self):
        p = self.new_project(
            (1, 2, 3),
            ((1, 2), (2, 3), (1, 3))
        )

        p.remove_redundancies()

        self.assertHasDependency(p, 1, 2)
        self.assertHasDependency(p, 2, 3)
        self.assertHasNoDependency(p, 1, 3)

    def test_remove_redundancies_diamond(self):
        p = self.new_project(
            (1, 2, 3, 4),
            ((1, 2), (2, 4), (1, 3), (3, 4), (1, 4))
        )

        p.remove_redundancies()

        self.assertHasDependency(p, 1, 2)
        self.assertHasDependency(p, 2, 4)
        self.assertHasDependency(p, 1, 3)
        self.assertHasDependency(p, 3, 4)
        self.assertHasNoDependency(p, 1, 4)

    def test_remove_redundancies_double_classic(self):
        p = self.new_project(
            (1, 2, 3, 4),
            ((1, 4), (4, 3), (1, 3), (4, 2), (1, 2))
        )

        p.remove_redundancies()

        self.assertHasDependency(p, 1, 4)
        self.assertHasDependency(p, 4, 3)
        self.assertHasDependency(p, 4, 2)
        self.assertHasNoDependency(p, 1, 3)
        self.assertHasNoDependency(p, 1, 2)

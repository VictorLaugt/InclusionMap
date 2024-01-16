import unittest

from inclusion_map.back.target_parser import CTargetParser, PythonTargetParser

__all__ = (
    'TestCTargetParser', 'TestPythonTargetParser'
)


class TestCTargetParser(unittest.TestCase):
    def test_parse_include(self):
        ...

class TestPythonTargetParser(unittest.TestCase):
    def test_parse_absolute_import(self):
        ...

    def test_parse_relative_import(self):
        ...

#!/usr/bin/env python3
import unittest
import sys

from inclusion_map.back.tests.inclusion_instructions_tests import *
# from inclusion_map.back.tests.target_parser_tests import *
from inclusion_map.back.tests.project_dependencies_tests import *


if __name__ == '__main__':
    if '-v' not in sys.argv:
        sys.argv.append('-v')
    unittest.main()

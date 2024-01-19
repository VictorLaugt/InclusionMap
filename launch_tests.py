#!/usr/bin/env python3
import unittest
import sys

from inclusion_map.back.tests import *

if __name__ == '__main__':
    if '-v' not in sys.argv:
        sys.argv.append('-v')
    unittest.main()

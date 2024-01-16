import unittest

from inclusion_map.back.project_dependencies import BiMap

__all__ = (
    "TestBiMap",
)


class TestBiMap(unittest.TestCase):
    def test_bimap_contains(self):
        bimap = BiMap()
        bimap.add_key_value(1, 1)
        bimap.add_key_value(1, 2)
        bimap.add_key_value(2, 2)
        bimap.add_key_value(2, 6)
        bimap.add_key_value(2, 7)
        bimap.add_key_value(3, 3)
        bimap.add_key_value(3, 4)
        bimap.add_key_value(4, 5)
        bimap.add_key_value(5, 4)

        self.assertTrue(bimap.contains_key_value(1, 1))
        self.assertTrue(bimap.contains_key_value(1, 2))
        self.assertTrue(bimap.contains_key_value(2, 2))
        self.assertTrue(bimap.contains_key_value(2, 6))
        self.assertTrue(bimap.contains_key_value(2, 7))
        self.assertTrue(bimap.contains_key_value(3, 3))
        self.assertTrue(bimap.contains_key_value(3, 4))
        self.assertTrue(bimap.contains_key_value(4, 5))
        self.assertTrue(bimap.contains_key_value(5, 4))

        self.assertFalse(bimap.contains_key_value(94, 100))
        self.assertFalse(bimap.contains_key_value(2, 10))
        self.assertFalse(bimap.contains_key_value(10, 7))
        self.assertFalse(bimap.contains_key_value(2, 4))
        self.assertFalse(bimap.contains_key_value(6, 2))
        self.assertFalse(bimap.contains_key_value(1, 4))

    def test_bimap_add_then_get(self):
        bimap = BiMap()
        bimap.add_key_value(1, 1)
        bimap.add_key_value(1, 2)
        bimap.add_key_value(2, 2)
        bimap.add_key_value(2, 6)
        bimap.add_key_value(2, 7)
        bimap.add_key_value(3, 3)
        bimap.add_key_value(3, 4)
        bimap.add_key_value(4, 5)
        bimap.add_key_value(5, 4)

        self.assertEqual(bimap.get_values(1), {1, 2})
        self.assertEqual(bimap.get_values(2), {2, 6, 7})
        self.assertEqual(bimap.get_values(3), {3, 4})
        self.assertEqual(bimap.get_values(4), {5})

        self.assertEqual(bimap.get_keys(1), {1})
        self.assertEqual(bimap.get_keys(2), {1, 2})
        self.assertEqual(bimap.get_keys(3), {3})
        self.assertEqual(bimap.get_keys(4), {3, 5})
        self.assertEqual(bimap.get_keys(5), {4})
        self.assertEqual(bimap.get_keys(6), {2})
        self.assertEqual(bimap.get_keys(7), {2})

    def test_bimap_discard_then_get(self):
        bimap = BiMap()
        bimap.add_key_value(1, 2)
        bimap.add_key_value(2, 2)
        bimap.add_key_value(2, 6)
        bimap.add_key_value(2, 7)

        self.assertEqual(bimap.get_values(1), {2})
        self.assertEqual(bimap.get_values(2), {2, 6, 7})
        self.assertEqual(bimap.get_keys(2), {1, 2})
        self.assertEqual(bimap.get_keys(6), {2})
        self.assertEqual(bimap.get_keys(7), {2})

        bimap.discard_key_value(2, 6)

        self.assertEqual(bimap.get_values(1), {2})
        self.assertEqual(bimap.get_values(2), {2, 7})
        self.assertEqual(bimap.get_keys(2), {1, 2})
        self.assertFalse(bimap.get_keys(6))
        self.assertEqual(bimap.get_keys(7), {2})

        bimap.discard_key_value(1, 2)

        self.assertFalse(bimap.get_values(1))
        self.assertEqual(bimap.get_values(2), {2, 7})
        self.assertEqual(bimap.get_keys(2), {2})
        self.assertFalse(bimap.get_keys(6))
        self.assertEqual(bimap.get_keys(7), {2})

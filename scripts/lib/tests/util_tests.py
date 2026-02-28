import unittest

from urllib.parse import quote

from lib.util import (
    make_code,
)

class TestUtil(unittest.TestCase):

    def test_make_code(self):
        cases = [
            ('Chuppa Cross IV', 'chuppa-cross-iv'),
            ('Jérémy Côté', 'jeremy-cote'),
            ('Alex Gómez Berna', 'alex-gomez-berna'),
            ('嘉隆 井澤', quote('嘉隆 井澤')),
        ]

        for case in cases:
            self.assertEqual(make_code(case[0]), case[1])

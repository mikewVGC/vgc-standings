import unittest

from urllib.parse import quote

from lib.util import (
    make_code,
    make_mon_code,
    make_item_code,
    fix_mon_name,
    fix_nature,
    make_season_info_str,
    get_season_bookends,
    make_nice_date_str,
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


    def test_make_mon_code(self):
        cases = [
            ('Pikachu', 'pikachu'),
            ('Flutter Mane', 'fluttermane'),
            ('Ursaluna (Bloodmoon Form)', 'ursalunabloodmoonform'),
        ]

        for case in cases:
            self.assertEqual(make_mon_code(case[0]), case[1])


    # this is actually the same as make_mon_code, but the function is stupider
    def test_make_item_code(self):
        cases = [
            ('Covert Cloak', 'covertcloak'),
            ('Charizardite X', 'charizarditex'),
        ]

        for case in cases:
            self.assertEqual(make_item_code(case[0]), case[1])


    def test_fix_mon_name(self):
        cases = [
            ('Venomoth', 'Venomoth'),
            ('Tauros [Paldean Form - Aqua Breed]', 'Tauros-Paldea-Aqua'),
            ('Urshifu [Rapid Strike Form]', 'Urshifu-Rapid-Strike'),
            ('Gastrodon [East Sea]', 'Gastrodon'),
            ('Indeedee [Female]', 'Indeedee-F'), # sexism is real
            ('Meowstic [Male]', 'Meowstic'),
        ]

        for case in cases:
            self.assertEqual(fix_mon_name(case[0]), case[1])


    def test_fix_nature(self):
        cases = [
            ('Adamant', 'Adamant'),
            ('Naïve', 'Naive'),
        ]

        for case in cases:
            self.assertEqual(fix_nature(case[0]), case[1])


    def test_make_season_info_str(self):
        self.assertEqual(
            make_season_info_str({
                "naic": { "processed": True },
            }),
            "We've just started"
        )


    def test_get_season_bookends(self):
        first, last, worlds = get_season_bookends({
            "naic": { "code": "naic" },
            "regional-code": { "code": "regional-code" },
            "euic": { "code": "euic" },
            "worlds": { "code": "worlds" },
        })

        self.assertEqual(first['code'], "naic")
        self.assertEqual(last['code'], "euic")
        self.assertEqual(worlds['code'], "worlds")


    def test_make_nice_date_str(self):
        cases = [
            ('2024-10-10', '2024-10-11', "Oct. 10 - 11, 2024"),
            ('2025-05-31', '2025-06-01', "May 31 - Jun. 1, 2025"),
        ]

        for case in cases:
            self.assertEqual(make_nice_date_str(*case[:2]), case[2])

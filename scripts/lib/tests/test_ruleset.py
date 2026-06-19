import unittest

from lib.ruleset import (
    Ruleset,
    RulesetCollection,
)

class TestRuleset(unittest.TestCase):
    
    def test_create_empty_ruleset(self):
        ruleset = Ruleset()

        self.assertEqual(ruleset.name, "")
        self.assertEqual(ruleset.tera, False)


    def test_create_ruleset_collection(self):
        collection = RulesetCollection([
            Ruleset(name="Test Rules"),
        ])

        self.assertEqual(type(collection.get_ruleset("Test Rules")), Ruleset)
        self.assertEqual(collection.get_ruleset("No Rules"), None)


    def test_dump_ruleset(self):
        ruleset = Ruleset(
            name="Regulation I",
            game="Scarlet & Violet",
            mega=False,
            zmoves=False,
            dynamax=False,
            tera=True,
            natures=False,
            restricted=2,
        )

        self.assertEqual(ruleset.dump_info(), {
            'mega': False,
            'zmoves': False,
            'dynamax': False,
            'tera': True,
            'restricted': 2,
            'natures': False,
        })

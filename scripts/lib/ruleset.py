
import json

class Ruleset():
    def __init__(self, **kwargs) -> None:
        self.name = ""
        self.game = ""

        self.mega = False
        self.zmoves = False
        self.dynamax = False
        self.tera = False

        self.restricted = 0

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def dump_info(self):
        return {
            'mega': self.mega,
            'zmoves': self.zmoves,
            'dynamax': self.dynamax,
            'tera': self.tera,
            'restricted': self.restricted,
        }

class RulesetCollection():
    def __init__(self, rulesets:list[Ruleset]) -> None:
        self.rulesets = rulesets

    def get_ruleset(self, name:str) -> Ruleset | None:
        for ruleset in self.rulesets:
            if ruleset.name == name:
                return ruleset

        return None

def create_ruleset(rule_data):
    return Ruleset(**rule_data)

def load_rulesets():    
    rulesets = []
    with open("data/common/rulesets.json", encoding='utf8') as file:
        raw_rulesets = json.loads(file.read())

    for ruleset in raw_rulesets:
        rulesets.append(create_ruleset(ruleset))

    return RulesetCollection(rulesets)


from pathlib import Path


# this is basically just a gloified dict
class KeyMap:
    def __init__(self):
        self.map = {}
        self.data_path = Path("data/nginx")
        self.data_path.mkdir(parents=True, exist_ok=True)

    def add_mapping(self, key, value):
        self.map[key] = value

    def dump(self):
        with open(f"{self.data_path}/slugs.map", 'w') as file:
            for k, v in self.map.items():
                v = v.replace('"', '\\"').replace('$', '')
                file.write(f"\"{k}\" \"{v}\";\n")


import json
import os

class BuilderCache():

    def __init__(self, config:dict = {}, prod:bool = False) -> None:
        self.meta_ssi = []
        self.data = {}

        self.config = config
        self.prod = prod

        os.makedirs("data/builder", exist_ok=True)


    def add_meta_ssi(self, file:str, title:str, description:str) -> None:
        self.meta_ssi.append({
            "file": file,
            "title": title,
            "description": description,
        })


    def add_cache_data(self, name:str, data:dict) -> None:
        self.data[name] = data


    def save(self) -> None:
        cache_data = {
            'ssi': [],
        }

        for k, d in self.data.items():
            cache_data[k] = d

        for m in self.meta_ssi:
            cache_data['ssi'].append(m)

        indent = 0 if self.prod else 2

        with open("data/builder/cache", 'w') as cachefile:
            cachefile.write(
                json.dumps(cache_data, indent=indent)
            )


    def load(self) -> dict:
        cache = {}
        try:
            with open("data/builder/cache", 'r') as cachefile:
                cache = json.loads(cachefile.read())
        except FileNotFoundError:
            print("[BuilderCache] No cache file was found")

        return cache


import json
import importlib
import os

class Builder():

    def __init__(self, config:dict = {}, prod:bool = False, cache:dict = {}) -> None:
        self.config = config
        self.flags = {
            "prod": prod,
        }
        self.cache = cache
        self.refs = {}
        self.steps = []

        build_config = {}

        try:
            with open("build.json", 'r') as buildfile:
                config = json.loads(buildfile.read())
                build_config = config['builder']
        except FileNotFoundError:
            print("[Builder] build.json not found")

        for ref, dir_name in build_config['refs'].items():
            items = os.listdir(dir_name)
            self.refs[ref] = {}
            for item in items:
                if not os.path.isfile(f"{dir_name}/{item}"):
                    continue

                ref_name = item.split('.')[0]
                self.refs[ref][ref_name] = f"{dir_name}/{item}"

        print(json.dumps(self.refs, indent=2))

        self.build_steps(build_config)


    def build_steps(self, build_config):
        steps = build_config['steps']

        for step in steps:
            if step not in build_config:
                print(f"[Builder] step '{step}' not found in build.json")
                continue

            if 'skip' in build_config[step] and build_config[step]['skip']:
                continue

            self.build_step(build_config[step])


    def build_step(self, step_data:dict):
        step_type = step_data['type']

        if step_type == 'html':
            main_tpl = Template(self.refs['tpl'][step_data['base-ref']])

            if 'tokens' in step_data:
                for token_info in step_data['tokens']:
                    token_type = token_info['type']
                    search_val = token_info['token']
                    replace_val = ""

                    if token_type == 'flag':
                        flag_name = token_info['name']
                        flag_val = self.flags[flag_name]
                        for opt in token_info['values']:
                            if opt['value'] != flag_val:
                                continue

                            token_type = opt['type']
                            token_info = { **token_info, **opt }
                    
                    if token_type == 'tpl':
                        replace_val = Template(self.refs['tpl'][token_info['ref']]).compile()
                    elif token_type == 'file':
                        ...
                    elif token_type == 'value':
                        loc =  token_info['location']
                        if loc == "config":
                            replace_val = self.config[token_info['key']]
                        elif loc == "cache":
                            replace_val = json.dumps(self.cache[token_info['key']])
                    else:
                        print(f"[Template] Unknown token type '{token_type}'")

                    main_tpl.add_token(search_val, replace_val)

            self.steps.append(main_tpl)


    def build(self):
        for step in self.steps:
            #print(step.compile())
            ...


class Template():

    def __init__(self, source:str) -> None:
        self.source = source
        self.tokens = []


    def add_token(self, search_val:str, replace_val:str) -> None:
        self.tokens.append({
            "search": search_val,
            "replace": replace_val,
        })


    def compile(self) -> str:
        tpl = ""
        try:
            with open(self.source, "r") as file:
                tpl = file.read()
        except FileNotFoundError:
            print(f"[Template] Couldn't load '{self.source}'")

        for token in self.tokens:
            if token['replace'] == None:
                continue

            tpl = tpl.replace(token['search'], token['replace'])

        return tpl


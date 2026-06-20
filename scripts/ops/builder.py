
from __future__ import annotations

import json
import os
import shutil
import subprocess

from datetime import date

from ops.config import Config

class Builder():

    def __init__(self, config:Config, cache:dict = {}) -> None:
        self.config = config
        self.flags = {
            "mode": config.mode,
        }
        self.cache = cache
        self.refs = {}
        self.vars = {}
        self.steps = []

        self.common = {
            'html': {}
        }

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

        if 'vars' in build_config:
            for var_name, var_val in build_config['vars'].items():
                self.vars[var_name] = var_val

        if 'common' in build_config:
            for common_data in build_config['common']:
                common_type = common_data['type']
                self.common[common_type] = common_data

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
            if 'tokens' in self.common['html']:
                step_data['tokens'] = [ *self.common['html']['tokens'], *step_data['tokens'] ]

            main_tpl = self.build_html(step_data)
            self.steps.append(main_tpl)

        if step_type == 'command':
            self.run_command(step_data)

        if step_type == 'copy':
            self.copy_files(step_data)

        if step_type == 'batch':
            self.batch(step_data)


    def batch(self, step_data:dict):
        batch_type = step_data['batch_type']
        if batch_type == 'html':
            data_loc = step_data['location']

            loop_data = []
            if data_loc == 'cache':
                loop_data = self.cache[step_data['key']]

                for item in loop_data:
                    tokens = []
                    if 'tokens' in step_data:
                        for token_data in step_data['tokens']:
                            token = token_data.copy()
                            if token['location'] == "loop":
                                token['location'] = "value"
                                token['value'] = item[token_data['name']]
                                del token['name']

                            tokens.append(token)

                    self.steps.append(
                        self.build_html({
                            "base-ref": step_data['base-ref'],
                            "tokens": tokens,
                            "out": f"{step_data['out']}/{item['file']}.html",
                        })
                    )

        else:
            print(f"Unknown batch_type '{batch_type}'")


    def build_html(self, step_data:dict) -> Template:
        main_tpl = Template(
            self.refs['tpl'][step_data['base-ref']],
            step_data['out']
        )

        if 'tokens' not in step_data:
            return main_tpl

        for token_info in step_data['tokens']:
            token_type = token_info['type']
            search_val = token_info['token']
            replace_val = ""

            if token_type == 'flag':
                flag_val = self.flags[token_info['name']]
                for opt in token_info['values']:
                    if opt['value'] != flag_val:
                        continue

                    token_type = opt['type']
                    token_info = { **token_info, **opt }

            if token_type == 'tpl':
                replace_val = Template(self.refs['tpl'][token_info['ref']]).compile()
            elif token_type == 'file':
                with open(token_info['location'], "r") as file:
                    replace_val = file.read()
            elif token_type == 'filename':
                replace_val = token_info['location']
                if 'ts' in token_info:
                    file_time = os.path.getmtime(f"public/{replace_val}")
                    replace_val = f"{replace_val}?{file_time}"
            elif token_type == 'value':
                loc =  token_info['location']
                if loc == 'config':
                    replace_val = self.config.get_by_token(token_info['key'])
                elif loc == 'cache':
                    if token_info['key'] in self.cache:
                        replace_val = json.dumps(self.cache[token_info['key']])
                elif loc == 'value':
                    replace_val = token_info[loc]
            elif token_type == 'date':
                if token_info['value'] == 'year':
                    replace_val = date.today().year
            else:
                print(f"[Template] Unknown token type '{token_type}'")

            main_tpl.add_token(search_val, replace_val)

        return main_tpl


    def run_command(self, step_data:dict):
        if not self._eval_condition(step_data):
            return

        subprocess.run(step_data['run'], capture_output=True)

        if 'set-vars' in step_data:
            for var_name, var_val in step_data['set-vars'].items():
                self.vars[var_name] = var_val


    def copy_files(self, step_data:dict):
        if not self._eval_condition(step_data):
            return

        copy_ops = {}

        for file_data in step_data['files']:
            f_type = file_data['type']
            f_ref = file_data['ref']
            full_ref = False
            if f_type in self.refs and f_ref in self.refs[f_type]:
                full_ref = self.refs[f_type][f_ref]
            else:
                print(f"Couldn't find ref '{f_type}/{f_ref}', skipping")

            if full_ref:
                copy_ops[full_ref] = file_data['dest']

        for src, dest in copy_ops.items():
            shutil.copy(src, dest)


    def build_meta_ssi(self) -> None:
        if 'ssi' not in self.cache:
            return

        with open("site/templates/head-ssi.html", 'r') as headssifile:
            ssi_base = headssifile.read()

            for ssi_data in self.cache['ssi']:
                main_ssi = ssi_base.replace('__TITLE__', ssi_data['title'])
                main_ssi = main_ssi.replace('__DESCRIPTION__', ssi_data['description'])

                with open(f"public/static/ssi/{ssi_data['file']}.html", 'w') as file:
                    file.write(main_ssi)


    def build(self):
        for step in self.steps:
            step.output()


    def _eval_condition(self, step_data:dict) -> bool:
        if 'condition' in step_data:
            condition = step_data['condition']

            if condition['type'] == "flag":
                flag_val = self.flags[condition['name']]
                if flag_val == condition['value']:
                    return True

        return False


class Template():

    def __init__(self, source:str, dest:str = "") -> None:
        self.source = source
        self.tokens = []
        self.dest = dest


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
            if token['replace'] is None:
                continue

            tpl = tpl.replace(token['search'], str(token['replace']))

        return tpl

    def output(self) -> None:
        compiled = self.compile()

        with open(self.dest, "w") as file:
            file.write(compiled)

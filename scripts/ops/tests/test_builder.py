import unittest
from unittest.mock import patch, mock_open

import json

from ops.builder import Builder
from ops.config import Config

"""
there's a lot more of this class that can be covered... it's not
really written in a way that's condusive to test coverage ... kinda
over-engineered, sorry
"""

class TestBuilder(unittest.TestCase):

    build_data = {
        "builder": {
            "steps": [
                "test_step",
            ],
            "refs": {
                "tpl": "../site/templates"
            },
            "test_step": {
                "type": "html",
                "base-ref": "home",
                "out": "public/index.html",
            }
        },
    }

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(build_data))
    def test_init_creates_steps(self, mock_file):

        builder = Builder(Config({}), {})

        self.assertEqual(len(builder.steps), 1)

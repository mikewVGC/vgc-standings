import unittest

from ops.config import Config

class TestConfig(unittest.TestCase):
    
    def test_init_config(self):

        config = Config({})

        self.assertEqual(config.mode, "dev")
        self.assertEqual(config.google_tag, "")


    def test_init_with_settings(self):

        config = Config({
            'mode': "prod",
            'monImgBase': "htts://some-url-here/images",
        })

        self.assertEqual(config.mode, "prod")
        self.assertEqual(config.mon_img_base, "htts://some-url-here/images")


    def test_get_by_token(self):

        config = Config({
            'googleTag': "ABCDEF",
        })

        self.assertEqual(config.google_tag, "ABCDEF")
        self.assertEqual(config.get_by_token("googleTag"), "ABCDEF")
        self.assertEqual(config.get_by_token("doesNotExist"), False)
        self.assertEqual(config.get_by_token("mode"), "dev")
